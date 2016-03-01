'''Automatic numbering script
This script does the following:
1. Updates the anchor tags to have the correct figure or table reference.
2. Updates the figure and table caption tags to have a prefix of table x: or figure x:.
3. Updates chapter titles, section titles and subsection titles.
Chapter titles need chapter x: as  a prefix, section titles need 'no. title shortcode'
subsection titles just need the shortcode at the end.
4. Numbers the worked examples.
5. Numbers the exercises
'''

# Import the necessary items
import os

from lxml import etree

'/home/heather/Desktop/books/mathematics-10/afrikaans/build/epubs/maths10/OPS/xhtml/maths10'
path = '/home/heather/Desktop/books/bookbuilder/scripts/tests/sample-files-for-testing/unnumbered_files'
file_list = os.listdir(path)
file_list.sort()


class NumberingClass():
    '''
    The workhorse for numbering all the pieces of the html
    '''

    def __init__(self, file_list):
        self.file_list = file_list
        self.numbered_files = {}
        self.section_number = 1
        self.figure_number = 1
        self.table_number = 1
        self.worked_example_number = 1
        self.exercise_number = 1
        self.table_dictionary = {}
        self.figure_dictionary = {}

    def number_files(self, write_back_to_file_boolean=False):
        for file_name in file_list:
            # Skip directories
            full_file_name = '{}/{}'.format(path, file_name)
            if os.path.isdir(full_file_name):
                continue
            # Files that do not start with a number
            # are not chapters
            if file_name[0] not in ['0', '1', '2']:
                continue
            self.numbered_files[full_file_name] = self.number_file(full_file_name)

        if not write_back_to_file_boolean:
            return

        for file_name in self.numbered_files.keys():
            if self.numbered_files[file_name]:
                full_file_name = '{}/{}'.format(path, file_name)
                file_text = self.number_file(file_name)
                self.write_back_to_file(file_text, file_name)

    def number_file(self, full_file_name):
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
            # Create the chapter titles
            if heading1 is not None:
                newText = 'Chapter {}: {}'.format(file_number, heading1.text)
                heading1.text = newText
            return xml

        file_counter = int(full_file_name[-17:-len('.cnxmlplus.html')])
        # this extracts the number at the tail end of the file name
        # Handle section, subsection, exercise, worked example, table and figure numbering

        def section_exercise_wex_counter(self, xml):
            if file_counter == 0:
                self.section_number = 1
                self.worked_example_number = 1
                self.exercise_number = 1
            for section in sections:
                if section.find('h3') is not None:  # subsection headings
                    h3 = section.find('h3')
                    try:
                        shortcode = etree.Element('span')
                        shortcode.text = '({})'.format(section.attrib['id'][2:])
                        shortcode.set('class', 'shortcode')
                        h3.text = '{} '.format(h3.text)
                        h3.append(shortcode)
                    except KeyError:
                        continue
                if section.attrib['class'] == 'worked_example':
                    title = section.find('h2')
                    if title is not None:
                        title.text = 'Worked example ' + str(self.worked_example_number) + ': ' + title.text
                        # this handles unicode errors better
                        self.worked_example_number += 1
                if section.attrib['class'] == 'exercises':  # exercises
                    try:
                        problem_set = section.find('.//div[@class]')
                        if problem_set.attrib['class'] == 'problemset':
                            span_code = etree.Element('span')
                            span_code.set('class', 'exerciseTitle')
                            span_code.text = 'Exercise {}.{}'.format(file_number, self.exercise_number)
                            problem_set.insert(0, span_code)
                            self.exercise_number += 1
                    except AttributeError:
                        continue
                if section.find('h2') is not None:  # section headings
                    h2 = section.find('h2')
                    try:
                        if section.attrib['id'] is not None and section.attrib['id'][:2] == 'sc':
                            shortcode = etree.Element('span')
                            shortcode.text = '({})'.format(section.attrib['id'][2:])
                            shortcode.set('class', 'shortcode')
                            h2.text = '{}.{} {} '.format(file_number, self.section_number, h2.text)
                            h2.append(shortcode)
                            self.section_number += 1
                    except KeyError:
                        continue
            return xml

        # figure numbering
        def figure_number_insert(self, xml):
            if file_counter == 0:
                self.figure_number = 1
            for figure in figures:
                caption = figure.find('.//figcaption')
                if caption is not None and figure.attrib['id'] is not None:
                    if caption.find('.//p') is not None:
                        para = caption.find('.//p')
                        para.text = 'Figure {}.{}: {}'.format(
                            file_number, self.figure_number, para.text)
                    else:
                        caption.text = 'Figure {}.{}: {}'.format(
                            file_number, self.figure_number, caption.text)
                    self.figure_dictionary[figure.attrib['id']] = str(
                        file_number) + '.' + str(self.figure_number)
                    self.figure_number += 1
            return xml

        # table numbering
        def table_number_insert(self, xml):
            if file_counter == 0:
                self.table_number = 1
            for div in divs:
                if div.attrib['class'] is not None:
                    try:
                        table_id = div.attrib['id']
                    except KeyError:
                        table_id = None
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
                            self.table_dictionary[div.attrib['id']] = str(file_number) + '.' + str(self.table_number)
                            self.table_number += 1
                #1/0
            return xml

        # replace the anchor tags
        def hyperlink_text_fix(self, xml):
            for anchor in anchors:
                try:
                    if anchor.attrib['class'] == 'InternalLink':
                        if anchor.attrib['href'][1:] in self.table_dictionary.keys():
                            anchor.text = 'Table ' + self.table_dictionary[anchor.attrib['href'][1:]]
                        elif anchor.attrib['href'][1:] in self.figure_dictionary.keys():
                            anchor.text = 'Figure ' + self.figure_dictionary[anchor.attrib['href'][1:]]
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
        # This overwrites the contents of the file you are working with.
        # Only do this if you are sure you can get the contents of the file back
        # before the script was run.

        with open(full_file_name, 'w') as file:
            file.write(file_text)
