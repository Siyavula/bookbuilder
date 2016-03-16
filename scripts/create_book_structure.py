'''
This code sets up a yaml file with the structure of a book
'''
import os
from lxml import etree
import yaml

path = '/home/heather/Desktop/books/physical-sciences-12/english'
fileList = os.listdir(path)
fileList.sort()

file_contents = ''

# loop over the files in the directory
for file_name in fileList:
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
    file_contents += '%s: \n' % chapter_title
    for j in section_list:
        file_contents += '  - %s \n' % j

# write the contents of each dictionary and list to a file
with open('test.txt', 'w') as file:
    file.write(file_contents)
    print yaml.load(file_contents)
