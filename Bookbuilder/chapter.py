from __future__ import print_function

import os
import logging
import hashlib
import subprocess
import shutil
import inspect
import sys

import lxml
from lxml import etree

try:
    from termcolor import colored
except ImportError:
    logging.error("Please install termcolor:\n sudo pip install termcolor")

from XmlValidator import XmlValidator
from XmlValidator import XmlValidationError
import pstikz2png
from pstikz2png import LatexPictureError
from . import htmlutils
from utils import mkdir_p


specpath = os.path.join(os.path.dirname(inspect.getfile(XmlValidator)),
                        'spec.xml')

DEBUG = False


def print_debug_msg(msg):
    '''prints a debug message if DEBUG is True'''
    if DEBUG:
        print(colored("DEBUG: {msg}".format(msg=msg), "yellow"))


class chapter(object):

    ''' Class to represent a single chapter
    '''

    def __init__(self, cnxmlplusfile, **kwargs):
        ''' cnxmlplusfile is the path of the file
        '''

        # set some default attributes.
        self.file = cnxmlplusfile
        self.chapter_number = None
        self.title = None
        self.hash = None
        self.has_changed = True
        self.valid = None
        self.output_formats = ['tex', 'html']

        # set attributes from keyword arguments
        # This can be used to set precomputed values e.g. read from a cache
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Parse the xml
        self.parse_cnxmlplus()

    def calculate_hash(self, content):
        ''' Calculates the md5 hash of the file content and returns it
        '''
        m = hashlib.md5()
        m.update(content)

        return m.hexdigest()

    def parse_cnxmlplus(self):
        ''' Parse the xml file and save some information
        '''
        with open(self.file, 'r') as f:
            content = f.read()

        if (self.hash is None) or (self.valid is False):
            self.hash = self.calculate_hash(content)
            # if the hash is None, it has not been passed from Book class and
            # hence didn't exist in the cache. Need to validate this file
            self.validate()
        else:
            # If self.hash has been set and it differs from current hash, then
            # re-validate
            current_hash = self.calculate_hash(content)
            if self.hash != current_hash:
                self.validate()
                self.hash = current_hash
                self.has_changed = True
            else:
                # file is valid, no validation required.
                self.valid = True
                self.hash = current_hash
                self.has_changed = False

        try:
            xml = etree.XML(content)
        except lxml.etree.XMLSyntaxError:
            logging.error(
                colored("{file} is not valid XML!".format(
                    file=self.file), 'red'))
            return None

        # save the number
        try:
            self.chapter_number = int(self.file[0:self.file.index('-')])
        except:
            self.chapter_number = 'N/A'
            logging.warn(
                "{file} doesn't follow naming convention \
                    CC-title-here.cnxmlplus".format(file=self.file))

        # The title should be in in an element called <title>
        # inside a <section type="chapter"> and there should only be one in the
        # file. For now.
        chapters = xml.findall('.//section[@type="chapter"]')
        if len(chapters) > 1:
            logging.error(
                "{filename} contains more than 1 chapter!".format(
                    filename=self.file))
        elif len(chapters) < 1:
            logging.error(
                "{filename} contains no chapters!".format(filename=self.file))
        else:
            self.title = chapters[0].find('.//title').text

    def info(self):
        ''' Returns a formatted string with all the details of the chapter
        '''
        info = '{ch}'.format(ch=self.chapter_number)
        info += ' ' * (4 - len(info))
        if self.valid:
            info += colored('OK'.center(8), 'green')
        else:
            info += colored('Not OK'.center(8), 'red')
        info += ' ' * (24 - len(info))
        info += '{file}'.format(file=self.file)

        return info

    def validate(self):
        ''' Run the validator on this file

        sets self.valid to True or False depending on the outcome
        '''
        print("Validating {f}".format(f=self.file))

        with open(self.file, 'r') as xmlfile:
            xml = xmlfile.read()
            # see if it is valid XML first
            try:
                etree.XML(xml)
            except etree.XMLSyntaxError:
                self.valid = False
                return
            # create an instance of the Validator
            xmlValidator = XmlValidator(open(specpath, 'rt').read())
            try:
                xmlValidator.validate(xml)
                self.valid = True
            except XmlValidationError as Err:
                print(Err)
                self.valid = False

    def __xml_preprocess(self, xml):
        ''' This is an internal method for the chapter class that tweaks the
        cnxmlplus before it is converted to one of the output formats e.g.
        image links are changed to point one folder up so that the output files
        in the build folder points to where the current images are located.

        This method is called from the convert method.

        input: cnxmlplus is an etree object of the cnxmlplus file
        output: etree object with pr

        '''
        # TODO add stuff here for tweaking
        processed_xml = xml

        return processed_xml

    def __copy_if_newer(self, src, dest):
        ''' Copy a file from src to  dest if src is newer than dest '''
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir):
            mkdir_p(dest_dir)

        if os.path.exists(src):
            # check whether src was modified more than a second after dest
            # and only copy if that was the case
            srcmtime = os.path.getmtime(src)
            try:
                destmtime = os.path.getmtime(dest)
                if srcmtime - destmtime > 1:
                    shutil.copy2(src, dest)
                    print_debug_msg("Copying {src} --> {dest}"
                                    .format(src=src, dest=dest))
            except OSError:
                # destination doesn't exist
                shutil.copy2(src, dest)
                print_debug_msg("Copying {src} --> {dest}"
                                .format(src=src, dest=dest))

        else:
            if not os.path.exists(dest):
                print(colored("WARNING! {src} cannot be found!"
                              .format(src=src), "magenta"))

    def __copy_tex_images(self, build_folder, output_path):
        ''' Find all images referenced in the cnxmlplus document and copy them
        to their correct relative places in the build/tex folder.

        '''
        with open(self.file) as f:
            xml = etree.XML(f.read())

        # if it is tex, we can copy the images referenced in the cnxmlplus
        # directly to the build/tex folder
        for image in xml.findall('.//image'):
            # find the src, it may be an attribute or a child element
            if 'src' in image.attrib:
                src = image.attrib['src'].strip()
            else:
                src = image.find('.//src').text.strip()

            # check for paths starting with /
            if src.startswith('/'):
                print(colored("ERROR! image paths may not start with /: ",
                              "red") + src)
                continue

            dest = os.path.join(build_folder, 'tex', src)
            if not os.path.exists(dest):
                try:
                    mkdir_p(os.path.dirname(dest))
                except OSError:
                    msg = colored("WARNING! {dest} is not allowed!"
                                  .format(dest=dest),
                                  "magenta")
                    print(msg)
            self.__copy_if_newer(src, dest)

    def __render_pstikz(self, output_path):
        ''' Use Bookbuilder/pstricks2png to render each pstricks and tikz
            image to png. Insert replace div.alternate tags with <img> tags
        '''
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
            codetext = ''.join([c for c in codetext if ord(c) < 128])
            codeHash = hashlib.md5(
                ''.join(codetext.encode('utf-8').split())).hexdigest()
            # see if the output png exists at
            # build/html/pspictures/hash.png  OR
            # build/html/tikzpictures/hash.png
            pngpath = os.path.join(os.path.dirname(output_path), pictype,
                                   codeHash+'.png')

            # copy to local image cache in .bookbuilder/images
            image_cache_path = os.path.join('.bookbuilder',
                                            pictype,
                                            codeHash+'.png')
            rendered = False
            # skip image generation if it exists
            if os.path.exists(image_cache_path):
                rendered = True

            if not rendered:
                # send this object to pstikz2png
                try:
                    if pre.attrib['class'] == 'pspicture':
                        figpath = pstikz2png.pspicture2png(pre, iDpi=150)
                    elif pre.attrib['class'] == 'tikzpicture':
                        figpath = pstikz2png.tikzpicture2png(pre, iDpi=150)
                except LatexPictureError:
                    print(colored("\nLaTeX failure", "red"))
                    print(etree.tostring(pre, pretty_print=True))
                    continue
                # done. copy to image cache
                self.__copy_if_newer(figpath, image_cache_path)
                # copy the pdf also.
                self.__copy_if_newer(figpath.replace('.png', '.pdf'),
                                     image_cache_path.replace('.png', '.pdf'))

                if not os.path.exists('figure.png'):
                    print("Problem :" + etree.tostring(pre))
            else:
                figpath = image_cache_path

            self.__copy_if_newer(image_cache_path, pngpath)

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

    def __copy_html_images(self, build_folder, output_path):
        ''' Find all images referenced in the converted html document and copy
        them to their correct relative places in the build/tex folder.

        '''
        # copy images directly included in cnxmlplus to the output folder
        with open(output_path, 'r') as f:
            html = etree.HTML(f.read())

        for img in html.findall('.//img'):
            src = img.attrib['src']
            dest = os.path.join(os.path.dirname(output_path), src)
            if not os.path.exists(src) and (not os.path.exists(dest)):
                print_debug_msg(src + " doesn't exist")

            self.__copy_if_newer(src, dest)

    def __tolatex(self):
        ''' Convert this chapter to latex
        '''
        print_debug_msg("Entered __tolatex {f}".format(f=self.file))
        myprocess = subprocess.Popen(["cnxmlplus2latex", self.file],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        latex, err = myprocess.communicate()

        return latex

    def __tohtml(self):
        ''' Convert this chapter to latex
        '''
        print_debug_msg("Entered __tohtml {f}".format(f=self.file))
#       tohtmlpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
#                                 'tohtml.py')
        myprocess = subprocess.Popen(["cnxmlplus2html", self.file],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        html, err = myprocess.communicate()

        return html

    def __toxhtml(self):

        xhtml = self.__tohtml()
        # Convert this html to xhtml
        xhtml = htmlutils.xhtml_cleanup(xhtml)

        return xhtml

    def convert(self, build_folder, output_format):
        ''' Convert the chapter to the specified output format and write the
        the build folder: {build_folder}/{output_format}/self.file.{format}
        e.g. build/tex/chapter1.cnxmlplus.tex

        output_format: one  of 'tex', 'html'
        '''
        conversion_functions = {'tex': self.__tolatex,
                                'html': self.__tohtml,
                                'xhtml': self.__toxhtml}

        for outformat in output_format:

            # convert this chapter to the specified format
            # call the converted method
            output_path = os.path.join(build_folder, outformat,
                                       self.file +
                                       '.{f}'.format(f=outformat))
            # only try this on valid cnxmlplus files
            if self.valid:
                # run the conversion only if the file has changed OR if it
                # doesn't exist (it may have been deleted manually)
                if (self.has_changed) or (not os.path.exists(output_path)):
                    mkdir_p(os.path.dirname(output_path))
                    print("Converting {ch} to {form}".format(ch=self.file,
                                                             form=outformat))
                    converted = conversion_functions[outformat]()
                    with open(output_path, 'w') as f:
                        f.write(converted)

                # file has not changed AND the file exists
                elif (not self.has_changed) and (os.path.exists(output_path)):
                    print("{f} {space} done {form}"
                          .format(f=self.file,
                                  space=' ' * (40 - len(self.file)),
                                  form=outformat))

                # copy the images to the build folder even if the file has not
                # changed and is still valid, the image may have been copied in
                # by the user
                if outformat == 'tex':
                    self.__copy_tex_images(build_folder, output_path)

                elif outformat == 'html':
                    # copy images included to the output folder
                    self.__copy_html_images(build_folder, output_path)
                    # read the output html, find all pstricks and tikz
                    # code blocks and render them as pngs and include them
                    # in <img> tags in the html
                    self.__render_pstikz(output_path)

                elif outformat == 'xhtml':
                    # copy images from html folder
                    self.__copy_html_images(build_folder, output_path)
                    self.__render_pstikz(output_path)

        return

    def __str__(self):
        chapno = str(self.chapter_number).ljust(4)
        return "{number} {title}".format(number=chapno, title=self.title)