"""
Usage:
    number_html5.py <path_name>

Options:
    path_name gives the path to the files that need to be numbered

Examples:
    number_html5.py home/heather/Desktop/books/mathematics-grade10/english/build/html5
"""

# Import the necessary items
import os
import sys
from docopt import docopt

from lxml import etree


class NumberingClass():
    """
    The workhorse for numbering all the pieces of the html
    This script does the following:
    1. Updates the anchor tags to have the correct figure or table reference.
    2. Updates the figure and table caption tags to
    have a prefix of table x: or figure x:.
    3. Updates chapter titles, section titles and subsection titles.
    Chapter titles need chapter x: as  a prefix, section titles need 'no.
    title shortcode' subsection titles just need the shortcode at the end.
    4. Numbers the worked examples.
    5. Numbers the exercises
    """

    def __init__(self, path):
        self.path = path
        self.file_list = os.listdir(self.path)
        self.file_list.sort()
        self.numbered_files = {}
        self.section_number = 1
        self.figure_number = 1
        self.table_number = 1
        self.worked_example_number = 1
        self.exercise_number = 1
        self.table_dictionary = {}
        self.figure_dictionary = {}

    def number_files(self, write_back_to_file_boolean=False):
        """
        Number files takes a boolean value to determine whether
        or not to write back to the input file.
        This function iterates over a directory containing html files
        and numbers sections, subsections, worked examples,
        exercises, tables and figures.
        This function overwrites the input file.
        """
        for file_name in self.file_list:
            # Skip directories
            full_file_name = '{}/{}'.format(self.path, file_name)
            if os.path.isdir(full_file_name):
                continue
            # Files that do not start with a number
            # are not chapters
            if file_name[0:2].isdigit():
                self.numbered_files[full_file_name] = self.number_file(full_file_name)

        if not write_back_to_file_boolean:
            return
        
        #import ipdb; ipdb.set_trace()
        
        for file_name in self.numbered_files.keys():
            if self.numbered_files[file_name]:
                file_text = self.numbered_files[file_name]
                self.write_back_to_file(file_text, file_name)

    def number_file(self, full_file_name):
        """
        This function first parses a given html5 file using etree and then
        extracts out relevant parts to modify in place.
        """
        xml = etree.parse(full_file_name, etree.HTMLParser())
        heading1 = xml.find('.//h1')
        sections = xml.findall('.//section')
        divs = xml.findall('.//div')
        figures = xml.findall('.//figure[@id]')
        anchors = xml.findall('.//a')
        find_chapter_number_index = full_file_name.rfind('/')
        file_number = int(full_file_name
            [find_chapter_number_index+1:find_chapter_number_index+3])

        def chapter_number_insert(self, xml):
            """Create the chapter titles"""
            if heading1 is not None:
                newText = 'Chapter {}: {}'.format(file_number, heading1.text)
                heading1.text = newText
            return xml
        
        cnxmlplus_file_name = os.path.splitext(full_file_name)[0]
        file_counter = int(os.path.splitext(cnxmlplus_file_name)[0][-2:])
        # this extracts the number at the tail end of the file name
        # this assumes that file names always have two extensions:
        # .cnxmlplus and .html, the first splitext removes the .html
        # the second splitext removes the .cnxmlplus

        def section_exercise_wex_counter(self, xml):
            """
            Number sections, append shortcodes to sections, append shortcodes to
            subsections, number exercise blocks, number worked example blocks.
            """
            if file_counter == 0:
                self.section_number = 1
                self.worked_example_number = 1
                self.exercise_number = 1
            for section in sections:
                if section.find('h3') is not None:  # subsection headings
                    h3 = section.find('h3')
                    if not section.attrib.get('id', None):
                        continue
                    shortcode = etree.Element('span')
                    shortcode.text = '({})'.format(section.attrib['id'][2:])
                    shortcode.set('class', 'shortcode')
                    h3.text = h3.text + ' '
                    h3.append(shortcode)
                if section.attrib['class'] == 'worked_example':
                    title = section.find('h2')
                    if title is not None:
                        title.text = 'Worked example ' + str(self.worked_example_number) + ': ' + title.text
                        # this handles unicode errors better
                        self.worked_example_number += 1
                if section.attrib['class'] == 'exercises':  # exercises
                    if section.find('.//div[@class]') is None:
                        continue
                    problem_set = section.find('.//div[@class]')
                    if problem_set.attrib['class'] == 'problemset':
                        span_code = etree.Element('span')
                        span_code.set('class', 'exerciseTitle')
                        span_code.text = 'Exercise {}.{}'.format(
                            file_number, self.exercise_number)
                        problem_set.insert(0, span_code)
                        self.exercise_number += 1
                if section.find('h2') is not None:  # section headings
                    h2 = section.find('h2')
                    if not section.attrib.get('id', None):
                        continue
                    if section.attrib['id'][:2] == 'sc':
                        shortcode = etree.Element('span')
                        shortcode.text = '({})'.format(section.attrib['id'][2:])
                        shortcode.set('class', 'shortcode')
                        h2.text = '{}.{} {} '.format(file_number, self.section_number, h2.text)
                        h2.append(shortcode)
                        self.section_number += 1
            return xml

        def figure_number_insert(self, xml):
            """Insert a figure number and the word figure prior to figure captions"""
            if file_counter == 0:
                self.figure_number = 1
            for figure in figures:
                caption = figure.find('.//figcaption')
                if caption is not None and figure.attrib['id'] is not None:
                    if caption.find('.//p') is not None:
                        para = caption.find('.//p')
                        if para.text is not None:
                            para.text = 'Figure ' + str(file_number) + '.' + str(self.figure_number) + ': ' + para.text
                    else:
                        if caption.text is not None:
                            caption.text = 'Figure ' + str(file_number) + '.' + str(self.figure_number) + ': ' + caption.text
                    self.figure_dictionary[figure.attrib['id']] = str(
                        file_number) + '.' + str(self.figure_number)
                    self.figure_number += 1
            return xml

        def table_number_insert(self, xml):
            """Insert a table number and the word table prior to table captions"""
            if file_counter == 0:
                self.table_number = 1
            for div in divs:
                if div.attrib.get('class', None):
                    if not div.attrib.get('id', None):
                        table_id = None
                    else:
                        table_id = div.attrib['id']
                    if table_id is not None and div.attrib['class'] == 'FigureTable':
                        caption = div.find('.//div[@class]')
                        if caption is not None and caption.attrib['class'] == 'caption':
                            if caption.find('.//p') is not None:
                                para = caption.find('.//p')
                                para.text = 'Table {}.{}: {}'.format(
                                    file_number, self.table_number, para.text)
                            else:
                                caption.text = 'Table {}.{}: {}'.format(
                                    file_number, self.table_number, caption.text)
                            self.table_dictionary[div.attrib['id']] = '{}.{}'.format(
                                str(file_number), str(self.table_number))
                            self.table_number += 1
            return xml

        def hyperlink_text_fix(self, xml):
            """Update only the anchor tags for internal links to have the relevant
            table or figure number"""
            for anchor in anchors:
                try:
                    if anchor.attrib['class'] == 'InternalLink':
                        if anchor.attrib['href'][1:] in self.table_dictionary.keys():
                            anchor.text = 'Table {}'.format(
                                self.table_dictionary[anchor.attrib['href'][1:]])
                        elif anchor.attrib['href'][1:] in self.figure_dictionary.keys():
                            anchor.text = 'Figure {}'.format(
                                self.figure_dictionary[anchor.attrib['href'][1:]])
                except KeyError:
                    continue
            return xml

        xml = chapter_number_insert(self, xml)
        xml = section_exercise_wex_counter(self, xml)
        xml = figure_number_insert(self, xml)
        xml = table_number_insert(self, xml)
        xml = hyperlink_text_fix(self, xml)

        file_text = None

        file_text = etree.tostring(xml, pretty_print=True)
        return file_text

    def write_back_to_file(self, file_text, full_file_name):
        """This overwrites the contents of the file you are working with.
        Only do this if you are sure you can get the contents of the file back
        before the script was run."""

        with open(full_file_name, 'w') as file:
            file.write(file_text)

if __name__ == '__main__':
    path = docopt(__doc__)['<path_name>']
    number_class = NumberingClass(path)
    number_class.number_files(True)
