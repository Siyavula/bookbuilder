'''
This code does the following three things:
1. Extracts the chapter titles and places them in a list of lists with the appropriate number.
2. Extracts the section shortcodes and places them in a dictionary. The key is the section number and the shortcode is the value
3. Extracts the subsection shortcodes and places them in a list.
'''
import os
from lxml import etree

path = '/home/heather/Desktop/books/physical-sciences-12/english'

# create all the lists and dictionaries that we need
chapter_list = []
section_dictionary = {}
subsection_list = []

# loop over the files in the directory
for file_name in os.listdir(path):

    full_file_name = '{}/{}'.format(path, file_name)
    
    # Skip directories
    if os.path.isdir(full_file_name):
        continue

    # now we have another issue: the directory does not only contain xml files, we need to remove those that do not contain xml and those that do not start with a number.
    if file_name[-9:] != 'cnxmlplus':
        continue
    if file_name[0] not in ['0', '1', '2', '3']:
        continue
    
    xml = etree.XML(open(full_file_name, 'r').read())

    chapter_number = int(file_name[:2])  # set the chapter number and make it an integer
    section_counter = 1  # start a section counter running
    subsection_counter = 1  # start a subsection counter running
    
    for section in xml.findall('.//section[@type]'):  # find all the sections
        if section.attrib['type'] == 'chapter':
            title = section.find('.//title')
            chapter_list.append([chapter_number, title.text])
        elif section.attrib['type'] == 'section':
            shortcode = section.find('.//shortcode')
            section_number = '{}.{}'.format(chapter_number, section_counter)
            section_dictionary[section_number] = 'sc{}'.format(shortcode.text)
            section_counter += 1
        elif section.attrib['type'] == 'subsection':
            shortcode = section.find('.//shortcode')
            subsection_number = '{}.{}'.format(chapter_number, subsection_counter)
            subsection_list.append('sc{}'.format(shortcode.text))
            subsection_counter += 1

# write the contents of each dictionary and list to a file
with open('gr12-science-toc.txt', 'w') as file:
    file.write(str(chapter_list))
    file.write('\n')
    file.write(str(section_dictionary))
    file.write('\n')
    file.write(str(subsection_list))
