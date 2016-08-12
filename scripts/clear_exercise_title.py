'''
This code does the following:
1. Finds all h2 with title Exercises
2. Removes them from the html
'''
import os
from lxml import etree

#path = '/home/heather/Desktop/books/physical-sciences-11/afrikaans/build/epubs/science11ccby/OPS/xhtml/science11'
path = '/home/heather/Desktop/books/mathematics-12/afrikaans/build/epubs/maths12ccby/OPS/xhtml/maths12'
#path = '/home/heather/Desktop/books/grade-10-lifescience-latex/afrikaans/build/epubs/lifescience10ccby/OPS/xhtml/lifescience10'
#path = '/home/heather/Desktop/books/scripts/test-files'

def exercise_cleaner(xml):
    for h2 in xml.findall('.//h2[@class]'):  # find all the h2's with class
        if h2.text == 'Exercises':
            h2.clear()  # clear the h2
    return xml

def practice_info_remove(xml):
    for span in xml.iter('span'):
        try:
            if (span.attrib['class'] == 'practiceInfo') or (span.attrib['class'] == 'shortcode'):
                span.getparent().remove(span)
        except KeyError:
            continue
    #for span in xml.findall('.//span'):
        ##tempText = span.text
        ##tempId = span.attrib['class']
        ##tempTail = span.tail
        #if span.attrib['class'] == 'practiceInfo':
            #span.clear()  # clear the span
    return xml

# loop over the files in the directory
for file_name in os.listdir(path):

    full_file_name = '{}/{}'.format(path, file_name)

    # Skip directories
    if os.path.isdir(full_file_name):
        continue

    xml = etree.HTML(open(full_file_name, 'r').read())

    fileText = None

    #xml = exercise_cleaner(xml)
    xml = practice_info_remove(xml)

    fileText = etree.tostring(xml, pretty_print=True)

    # target_filename = '{}/heather.txt'.format(path)

    if fileText != None:
        with open(full_file_name, 'w') as file:
            file.write(fileText)
