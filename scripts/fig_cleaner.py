'''
This code does the following:
1. Fixes the broken href tags for figures
'''
import os
from lxml import etree

path = '/home/heather/Desktop/books/physical-sciences-12/afrikaans/build/epubs/science12/OPS/xhtml/science12'
#path = '/home/heather/Desktop/books/scripts/test-files/new_test'

def fig_ref_fix(xml):
    for a in xml.findall('.//a'):  # find all the a tags
        tempText = a.text
        tempId = a.attrib['href']
        tempTail = a.tail
        try:
            if a.text[:3] != 'css' or a.text[:3] != 'htt':  # trying to remove the css and http links
                a.clear()  # clear the a tag
                a.text = tempText
                tempId = tempId.replace(':', '-')
                a.set('href', tempId)
                a.tail = tempTail
        except TypeError:
            continue
    return xml

# loop over the files in the directory
for file_name in os.listdir(path):

    full_file_name = '{}/{}'.format(path, file_name)

    # Skip directories
    if os.path.isdir(full_file_name):
        continue

    xml = etree.HTML(open(full_file_name, 'r').read())

    fileText = None

    xml = fig_ref_fix(xml)

    fileText = etree.tostring(xml, pretty_print=True)

    # target_filename = '{}/heather.txt'.format(path)

    if fileText != None:
        with open(full_file_name, 'w') as file:
            file.write(fileText)
