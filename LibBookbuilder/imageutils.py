"""
This module contains functions that does convertion of code and equations to
PDF and png formats

"""

from __future__ import print_function
import os
import sys
import hashlib
import errno
import shutil
from xml.sax.saxutils import unescape

from lxml import etree
from termcolor import colored

from . import pstikz2png
from .pstikz2png import LatexPictureError
from . import utils


def get_code_hash(codetext):
    '''
    Calculate the hash and output path for a given image, given the code as
    string
    '''
    codetext = ''.join([c for c in codetext if ord(c) < 128])
    code_hash = hashlib.md5(
        ''.join(codetext.encode('utf-8').split())).hexdigest()

    return code_hash


def cleanup_after_latex(figpath):
    ''' clean up after the image generation
    '''
    tmpdir = os.path.dirname(figpath)
    try:
        shutil.rmtree(tmpdir)
    except OSError as exc:
        if exc.errno != errno.ENOENT:  # ENOENT - no such file or directory
            raise  # re-raise exception


def run_latex(data):
    ''' Run the image generation for pstricks and tikz images
    '''
    pictype, codehash, codetext = data
    # copy to local image cache in .bookbuilder/images
    image_cache_path = os.path.join('.bookbuilder',
                                    pictype,
                                    codehash+'.png')
    rendered = False
    # skip image generation if it exists
    if os.path.exists(image_cache_path):
        rendered = True
        sys.stdout.write('s')

    if not rendered:
        sys.stdout.write('.')
        # send this object to pstikz2png
        try:
            if pictype == 'pspicture':
                figpath = pstikz2png.pspicture2png(codetext, iDpi=150)
            elif pictype == 'tikzpicture':
                figpath = pstikz2png.tikzpicture2png(codetext, iDpi=150)
            elif pictype == 'equation':
                figpath = pstikz2png.equation2png(codetext, iDpi=150)

        except LatexPictureError as lpe:
            print(colored("\nLaTeX failure", "red"))
            print(unicode(lpe))
            return None

        if figpath:
            # done. copy to image cache
            utils.copy_if_newer(figpath, image_cache_path)
            # copy the pdf also but run pdfcrop first
            utils.copy_if_newer(figpath.replace('.png', '.pdf'),
                                image_cache_path.replace('.png', '.pdf'))

            cleanup_after_latex(figpath)
    else:
        figpath = image_cache_path

    sys.stdout.flush()
    return image_cache_path


def _render_html_images(html, output_path, parallel=True):
    ''' Given etree object of the html file, render images and change the
    DOM tp have image links. Returns Etree object
    '''
    valid = True
    # find all the pspicture and tikz elements
    pspics = [p for p in html.findall('.//pre[@class="pspicture"]')]
    tikzpics = [p for p in html.findall('.//pre[@class="tikzpicture"]')]
    allpics = pspics + tikzpics

    # create a data list for the Pool map to work on
    pooldata = []
    for pre in allpics:
        pictype = pre.attrib['class']
        # find the hash of the code content
        codetext = pre.find('.//code').text
        code_hash = get_code_hash(codetext)
        # see if the output png exists at
        # build/html/pspictures/hash.png  OR
        # build/html/tikzpictures/hash.png
        pooldata.append((pictype, code_hash, codetext))

    if pooldata:
        # call parallel map
        image_cache_paths = utils.Map(run_latex, pooldata, parallel=False)

        for (pre, pooldata, icp) in zip(allpics, pooldata, image_cache_paths):
            image_cache_path = icp
            if not image_cache_path:
                valid = False
                continue
            pictype, code_hash, codetext = pooldata
            pngpath = os.path.join(os.path.dirname(output_path), pictype,
                                   code_hash+'.png')
            utils.copy_if_newer(image_cache_path, pngpath)

            # replace div.alternate with <img>
            parent = pre.getparent().getparent()
            img = etree.Element('img')
            img.attrib['src'] = os.path.join(pictype, code_hash+'.png')
            img.attrib['alt'] = code_hash + '.png'
            parent.replace(pre.getparent(), img)
#           figure.remove(pre.getparent())

    return html, valid


def _render_tex_images(tex, output_path, parallel=True):
    '''
    Given TeX file as string, find pstricks and tikz images and generate
    the PDF version, include in file as graphics, return as string
    '''
    valid = True
    environments = ['pspicture', 'tikzpicture']
    for pictype in environments:
        texsplit = tex.split(r'\begin{{{env}}}'.format(env=pictype))
        pooldata = []

        for i, chunk in enumerate(texsplit[1:]):
            env_end = chunk.find(r'\end{{{env}}}'.format(env=pictype))
            # get code text and hash
            codetext = chunk[0:env_end]
            code_hash = get_code_hash(codetext)
            pooldata.append((pictype, code_hash, codetext))

        if pooldata:
            # call parallel map
            image_cache_paths = utils.Map(run_latex, pooldata,
                                          parallel=parallel)

            for i, (chunk, pooldata, icp) in enumerate(zip(texsplit[1:],
                                                           pooldata,
                                                           image_cache_paths)):
                if not icp:
                    valid = False
                    # Image was not valid
                    continue

                pictype, code_hash, codetext = pooldata
                env_end = chunk.find(r'\end{{{env}}}'.format(env=pictype))
                image_cache_path = icp
                # place where image will go.
                pdfpath = os.path.join(os.path.dirname(output_path),
                                       pictype, code_hash+'.pdf')
                # This returns the png path
                pdf_cache_path = image_cache_path.replace('.png', '.pdf')
                # copy generated pdf to tex folder.
                utils.copy_if_newer(pdf_cache_path, pdfpath)

                # replace environment with \includegraphics
                newenv = \
                    r'\includegraphics{{{f}}}'.format(
                        f=os.path.join(pictype,
                                       code_hash + '.pdf'))
                endlength = len(r'\end{{{env}}}'.format(env=pictype))
                texsplit[i+1] = newenv + chunk[env_end + endlength:]
            tex = ''.join(texsplit)

    return tex, valid


def _render_mobile_images(html, output_path, parallel=True):
    '''
    Given HTML file as string, equations and generate png images for them.
    '''
    valid = True
    pictype = 'equation'
    environments = [(r'\(', r'\)'),
                    (r'\[', r'\]'),
                    (r'\begin{align*}', r'\end{align*}')]
    for (env_start, env_end) in environments:
        htmlsplit = html.split(env_start)
        pooldata = []

        for i, chunk in enumerate(htmlsplit[1:]):
            # This finds stuff like
            #
            # \[ blah \\[8pt] \]
            #          ^ this is seen as start for new equation
            # must avoid that corner case
            env_end_pos = chunk.find(env_end)
            # get code text and hash
            codetext = chunk[0:env_end_pos]
            code_hash = get_code_hash(codetext)
            # unescape the code for latex generation
            codetext = unescape(codetext)
            pooldata.append((pictype,
                             code_hash,
                             env_start + codetext + env_end))

        if pooldata:
            # call parallel map
            image_cache_paths = utils.Map(run_latex, pooldata,
                                          parallel=parallel)

            for i, (chunk, pooldata, icp) in enumerate(zip(htmlsplit[1:],
                                                           pooldata,
                                                           image_cache_paths)):
                if not icp:
                    valid = False

                pictype, code_hash, codetext = pooldata
                env_end_pos = chunk.find(env_end)
                image_cache_path = icp
                # place where image will go.
                pngpath = os.path.join(os.path.dirname(output_path),
                                       pictype, code_hash+'.png')
                # This returns the png path
                # copy generated pdf to tex folder.
                utils.copy_if_newer(image_cache_path, pngpath)

                # replace environment with img tag
                # must specify block or inline
                if env_start == r'\(':
                    imgclass = 'math-inline'
                else:
                    imgclass = 'math-block'
                newenv = \
                    r'<img class="{imgclass}" src="{f}"/>'.format(
                        imgclass=imgclass,
                        f=os.path.join(pictype,
                                       code_hash + '.png'))
                endlength = len(env_end)
                htmlsplit[i+1] = newenv + chunk[env_end_pos + endlength:]
            html = ''.join(htmlsplit)

    return html, valid


def render_images(output_path, parallel=True):
    ''' Given an output path, find all the tikz and pstricks images and render
    them as pdf and png. This function act as delegator for the pstikz2png
    module
    '''

    #
    # html, xhtml and mobile output
    #
    if output_path.endswith('html'):
        with open(output_path, 'r') as htmlout:
            html = etree.HTML(htmlout.read().decode('utf-8'))

        html, valid = _render_html_images(html, output_path, parallel=parallel)

        with open(output_path, 'w') as htmlout:
            htmlout.write(etree.tostring(html, method='xml').encode('utf-8'))

    #
    # TeX output
    #
    if output_path.endswith(".tex"):
        with open(output_path, 'r') as texout:
            tex = texout.read()

        tex, valid = _render_tex_images(tex, output_path, parallel=parallel)
        with open(output_path, 'w') as texout:
            texout.write(tex)

    #
    # Mobile html, equations need to be rendered to images
    #
    if r'/mobile/' in output_path:
        with open(output_path, 'r') as htmlout:
            html = htmlout.read()

        html, valid = _render_mobile_images(html, output_path,
                                            parallel=parallel)

        with open(output_path, 'w') as htmlout:
            htmlout.write(html)
    sys.stdout.write('\n')
    sys.stdout.flush()
    return valid
