'''
This script extracts the worked examples from book files.
The titles are added to the dictionary with the appropriate number.
'''
import os
from lxml import etree

path = '/home/heather/Desktop/books/physical-sciences-11/afrikaans'

wex_dictionary = {}
for file_name in os.listdir(path):

    full_file_name = '{}/{}'.format(path, file_name)
    
    # Skip directories
    if os.path.isdir(full_file_name):
        continue

    # now we have another issue: the directory does not only contain xml files, we need to remove those that do not contain xml.
    if file_name[-9:] != 'cnxmlplus':
        continue
    
    xml = etree.XML(open(full_file_name, 'r').read())
    
    wex_counter = 1  # set a counter
    
    for wex in xml.findall('.//worked_example'):  # find all the worked examples
        title = wex.find('.//title')  # find and extract the title
        title = title.text  # this should in theory just give me the text
        wex_dictionary[title] = wex_counter  # create a python dictionary with the title as the key and the number as the value
        wex_counter += 1  # increment the counter
        # rinse and repeat

# write the contents of the dictionary
with open('gr12-science-wexes.txt', 'w') as file:
    file.write(str(wex_dictionary))
