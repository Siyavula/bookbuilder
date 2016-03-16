'''
This code sets up a yaml file with the structure of a book
'''
import os
from lxml import etree
import yaml

path = '/home/heather/Desktop/books/physical-sciences-12/english'
file_list = os.listdir(path)
file_list.sort()

class BookStructureCreation():
    """
    This class extracts the book structure information into a yaml file
    """
    def __init__(self, file_list):
        self.file_list = file_list
        self.file_contents = ''
    
    def create_structure(self):
        file_contents = self.section_chapter_extract()
        self.write_to_yaml_file(file_contents)
    
    def section_chapter_extract(self):
        for file_name in self.file_list:
            full_file_name = '{}/{}'.format(path, file_name)
            
            # Skip directories
            if os.path.isdir(full_file_name):
                continue

            # we need to remove files that do not contain xml
            # and files that do not start with a number
            if file_name[-9:] != 'cnxmlplus':
                continue
            if file_name[0] not in ['0', '1', '2', '3']:
                continue
            
            xml = etree.XML(open(full_file_name, 'r').read())
            
            section_list = []
            for section in xml.findall('.//section[@type]'):
                if section.attrib['type'] == 'chapter':
                    title = section.find('.//title')
                    chapter_title = title.text
                elif section.attrib['type'] == 'section':
                    title = section.find('.//title')
                    text = title.text
                    text = text.replace(':', '-')
                    section_list.append(text)
            self.file_contents += '%s: \n' % chapter_title
            for section in section_list:
                self.file_contents += '  - %s \n' % section
        return self.file_contents
    
    def write_to_yaml_file(self, file_contents):
        # write the contents of each dictionary and list to a file
        with open('test.txt', 'w') as file:
            file.write(file_contents)
            #print yaml.load(file_contents)

book_structure = BookStructureCreation(file_list)
print book_structure.create_structure()
