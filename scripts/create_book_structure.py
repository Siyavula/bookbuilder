"""
Usage:
    create_book_structure.py <path_name>

Options:
    path_name gives the path to the files that need to be numbered

Examples:
    create_book_structure.py '/home/books/grade-10-mathslit-latex/english'

"""
import os
import sys
from docopt import docopt
from lxml import etree
import yaml


class BookStructureCreation():
    """
    This class extracts the book structure information into a yaml file
    """
    def __init__(self, path):
        self.path = path
        self.file_list = os.listdir(self.path)
        self.file_list.sort()
        self.file_contents = ''
        self.book_data = ''

    def create_structure(self, write_back_to_file_boolean=False):
        self.book_data += self.section_chapter_extract(self.file_list, self.path)

        if not write_back_to_file_boolean:
            return

        self.write_to_yaml_file(self.book_data)
    
    def fix_title_punctuation(self, title):
        """Replace : in titles with the correct yaml format"""
        return title.replace(':', '":"')
    
    def fix_file_name(self, file_name):
        """Replace punctuation in the file name and remove the extra pieces"""
        file_name = file_name.split('.')[0]
        file_name = file_name.replace(',', '').replace("'", '').replace(':', '')
        return file_name

    def section_chapter_extract(self, file_list, path):
        self.file_contents += 'chapters: \n'
        for file_name in self.file_list:
            full_file_name = '{}/{}'.format(self.path, file_name)

            # Skip directories
            if os.path.isdir(full_file_name):
                continue

            # we need to remove files that do not contain xml
            # and files that do not start with a number
            if not file_name.endswith('cnxmlplus'):
                continue
            if not file_name[0].isdigit():
                continue

            xml = etree.parse(full_file_name, etree.HTMLParser())
            chapter_number = int(file_name[:2])
            section_list = []
            section_list_links = []
            section_number = 1

            for section in xml.findall('.//section[@type]'):
                if section.attrib['type'] == 'chapter':
                    chapter_title = section.find('.//title')
                    self.file_contents += '  - number: {} \n'.format(
                        chapter_number)
                    self.file_contents += '    title: ' + self.fix_title_punctuation(chapter_title.text) + ' \n'
                    self.file_contents += '    title-link: ' + self.fix_file_name(file_name[3:]) + ' \n'
                elif section.attrib['type'] == 'section':
                    title = section.find('.//title')
                    title_text = title.text
                    title_text = title_text.replace(':', '":"')
                    section_title = str(chapter_number) + '.' + str(section_number) + ' ' + self.fix_title_punctuation(title_text)
                    if section_number - 1 < 10:
                        section_title_link = self.fix_file_name(file_name) + '-0' + str(section_number - 1)
                    else:
                        section_title_link = self.fix_file_name(file_name) + '-' + str(section_number - 1)
                    section_number += 1
                    section_list.append(section_title)
                    section_list_links.append(section_title_link)
            self.file_contents += '    sections: \n'
            for i in section_list:
                self.file_contents += '      - ' + i + ' \n'
            self.file_contents += '    sections-links: \n'
            for i in section_list_links:
                self.file_contents += '      - ' + i + ' \n'
        return self.file_contents

    def write_to_yaml_file(self, file_contents):
        with open('book-structure.txt', 'w') as file:
            file.write(file_contents)

if __name__ == "__main__":
    path = docopt(__doc__)['<path_name>']
    book_structure = BookStructureCreation(path)
    book_structure.create_structure(True)
