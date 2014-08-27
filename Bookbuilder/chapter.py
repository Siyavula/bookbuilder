from __future__ import print_function

import os
import logging
import hashlib
import subprocess
import inspect

import lxml
from lxml import etree

try:
    from termcolor import colored
except ImportError:
    logging.error("Please install termcolor:\n sudo pip install termcolor")

from XmlValidator import XmlValidator
from XmlValidator import XmlValidationError
from . import htmlutils
import imageutils
from utils import mkdir_p, copy_if_newer


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
        self.conversion_success = {'tex': False,
                                   'html': False,
                                   'xhtml': False,
                                   'mobile': False}

        # set attributes from keyword arguments
        # This can be used to set precomputed values e.g. read from a cache
        for key, value in kwargs.items():
            setattr(self, key, value)

        if not self.render_problems:
            # if this has not been instantiated yet create an empty
            # dict to keep track of image rendering success for every output
            # format. Make all True to force image generation on first go.
            self.render_problems = {'tex': True,
                                    'html': True,
                                    'xhtml': True,
                                    'mobile': True}
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
        with open(self.file, 'r') as f_in:
            content = f_in.read()

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
            except XmlValidationError as err:
                print(err)
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
        processed_xml = xml

        return processed_xml

    def __copy_tex_images(self, build_folder, output_path):
        ''' Find all images referenced in the cnxmlplus document and copy them
        to their correct relative places in the build/tex folder.

        '''
        success = True
        with open(self.file) as f_in:
            xml = etree.XML(f_in.read())

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
                success = False
                continue

            dest = os.path.join(build_folder, 'tex', src)
            if not os.path.exists(dest):
                try:
                    mkdir_p(os.path.dirname(dest))
                except OSError:
                    msg = colored("WARNING! {dest} is not allowed!"
                                  .format(dest=dest),
                                  "magenta")
                    success = False
                    print(msg)
            success = copy_if_newer(src, dest)

        return success

    def __render_pstikz(self, output_path, parallel=True):
        ''' Use Bookbuilder/pstricks2png to render each pstricks and tikz
            image to png. Insert replace div.alternate tags with <img> tags
            Also, find pstricks and tikz in tex output and replace with
            includegraphics{}
        '''
        rendered = imageutils.render_images(output_path, parallel=parallel)

        return rendered

    def __copy_html_images(self, build_folder, output_path):
        ''' Find all images referenced in the converted html document and copy
        them to their correct relative places in the build/tex folder.

        '''
        success = True
        # copy images directly included in cnxmlplus to the output folder
        with open(output_path, 'r') as f_in:
            html = etree.HTML(f_in.read())

        for img in html.findall('.//img'):
            src = img.attrib['src']
            dest = os.path.join(os.path.dirname(output_path), src)
            if not os.path.exists(src) and (not os.path.exists(dest)):
                print_debug_msg(src + " doesn't exist")

            success = copy_if_newer(src, dest)

        return success

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
        html = htmlutils.add_mathjax(html)
#       html = htmlutils.repair_equations(html)

        return html

    def __toxhtml(self):
        ''' Convert this chapter to html'''

        xhtml = self.__tohtml()
        # Convert this html to xhtml
        xhtml = htmlutils.xhtml_cleanup(xhtml)

        return xhtml

    def __tomobile(self):
        ''' Conver this chapter to xhtml'''
        html = self.__toxhtml()

        return html

    def convert(self, build_folder, output_format, parallel=True):
        ''' Convert the chapter to the specified output format and write the
        the build folder: {build_folder}/{output_format}/self.file.{format}
        e.g. build/tex/chapter1.cnxmlplus.tex

        output_format: one  of 'tex', 'html'
        '''
        conversion_functions = {'tex': self.__tolatex,
                                'html': self.__tohtml,
                                'xhtml': self.__toxhtml,
                                'mobile': self.__tomobile}

        for outformat in output_format:

            # convert this chapter to the specified format
            # call the converted method
            output_path = os.path.join(build_folder, outformat,
                                       self.file +
                                       '.{f}'.format(f=outformat))

            if outformat == 'mobile':
                output_path = output_path.replace(r'.mobile', '.html')

            # only try this on valid cnxmlplus files
            if self.valid:
                # run the conversion only if the file has changed OR if it
                # doesn't exist (it may have been deleted manually)
                if any((self.has_changed,
                        not os.path.exists(output_path),
                        self.render_problems[outformat])):

                    mkdir_p(os.path.dirname(output_path))
                    print("Converting {ch} to {form}".format(ch=self.file,
                                                             form=outformat))
                    converted = conversion_functions[outformat]()
                    with open(output_path, 'w') as f_out:
                        # convert tabs to spaces
                        f_out.write(converted)

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
                    copy_success = self.__copy_tex_images(build_folder,
                                                          output_path)
                    rendered = self.__render_pstikz(output_path,
                                                    parallel=parallel)

                elif outformat == 'html':
                    # copy images included to the output folder
                    copy_success = self.__copy_html_images(build_folder,
                                                           output_path)
                    # read the output html, find all pstricks and tikz
                    # code blocks and render them as pngs and include them
                    # in <img> tags in the html
                    rendered = self.__render_pstikz(output_path,
                                                    parallel=parallel)

                elif outformat == 'xhtml':
                    # copy images from html folder
                    copy_success = self.__copy_html_images(build_folder,
                                                           output_path)
                    rendered = self.__render_pstikz(output_path,
                                                    parallel=parallel)

                elif outformat == 'mobile':
                    # copy images from html folder
                    copy_success = self.__copy_html_images(build_folder,
                                                           output_path)
                    rendered = self.__render_pstikz(output_path,
                                                    parallel=parallel)

                if not (rendered and copy_success):
                    self.render_problems = True
                else:
                    self.render_problems = False

    def __str__(self):
        chapno = str(self.chapter_number).ljust(4)
        return "{number} {title}".format(number=chapno, title=self.title)
