import os
import sys
import hashlib

from lxml import etree
from termcolor import colored

import pstikz2png
from pstikz2png import LatexPictureError
import utils


def get_code_hash(codetext):
    '''
    Calculate the hash and output path for a given image, given the code as
    string
    '''
    codetext = ''.join([c for c in codetext if ord(c) < 128])
    codeHash = hashlib.md5(
        ''.join(codetext.encode('utf-8').split())).hexdigest()

    return codeHash


def run_latex(pictype, codehash, codetext):
    ''' Run the image generation for pstricks and tikz images
    '''
    # copy to local image cache in .bookbuilder/images
    image_cache_path = os.path.join('.bookbuilder',
                                    pictype,
                                    codehash+'.png')
    rendered = False
    # skip image generation if it exists
    if os.path.exists(image_cache_path):
        rendered = True

    if not rendered:
        # send this object to pstikz2png
        try:
            if pictype == 'pspicture':
                figpath = pstikz2png.pspicture2png(codetext, iDpi=150)
            elif pictype == 'tikzpicture':
                figpath = pstikz2png.tikzpicture2png(codetext, iDpi=150)
        except LatexPictureError:
            print(colored("\nLaTeX failure", "red"))
            print(codetext)
            pass

        # done. copy to image cache
        utils.copy_if_newer(figpath, image_cache_path)
        # copy the pdf also.
        utils.copy_if_newer(figpath.replace('.png', '.pdf'),
                            image_cache_path.replace('.png', '.pdf'))

        if not os.path.exists('figure.png'):
            print("Problem :\n" + codetext)
    else:
        figpath = image_cache_path

    return image_cache_path


def render_images(output_path):
    ''' Given an output path, find all the tikz and pstricks images and render
    them as pdf and png. This function act as delegator for the pstikz2png
    module
    '''

    if output_path.endswith('html'):
        with open(output_path, 'r') as htmlout:
            html = etree.HTML(htmlout.read())

        # find all the pspicture and tikz elements
        pspics = [p for p in html.findall('.//pre[@class="pspicture"]')]
        tikzpics = [p for p in html.findall('.//pre[@class="tikzpicture"]')]
        allpics = pspics + tikzpics

        for i, pre in enumerate(allpics):
            msg = "  Generating image {n} / {d}\r".format(n=i+1,
                                                          d=len(allpics))
            sys.stdout.write(msg)
            sys.stdout.flush()

            pictype = pre.attrib['class']
            # find the hash of the code content
            codetext = pre.find('.//code').text
            codeHash = get_code_hash(codetext)
            # see if the output png exists at
            # build/html/pspictures/hash.png  OR
            # build/html/tikzpictures/hash.png
            pngpath = os.path.join(os.path.dirname(output_path), pictype,
                                   codeHash+'.png')
            image_cache_path = run_latex(pictype, codeHash, codetext)
            utils.copy_if_newer(image_cache_path, pngpath)

            # replace div.alternate with <img>
            figure = pre.getparent().getparent()
            img = etree.Element('img')
            img.attrib['src'] = os.path.join(pictype, codeHash+'.png')
            img.attrib['alt'] = codeHash + '.png'
            figure.append(img)
            figure.remove(pre.getparent())
            # clean up
            for f in ["figure-autopp.cb",
                      "figure.aux",
                      "figure.cb",
                      "figure.cb2",
                      "figure.epsi",
                      "figure.log",
                      "figure.pdf",
                      "figure-pics.pdf",
                      "figure.png",
                      "figure.ps",
                      "figure.tex"]:
                if os.path.exists(f):
                    os.remove(f)

        with open(output_path, 'w') as htmlout:
            htmlout.write(etree.tostring(html, method='xml'))
