'''
This code does the following:
Extracts the figure attributions and puts them in a list
'''
import os
from lxml import etree

path = '/home/heather/Desktop/books/grade-10-lifescience-latex/english'

# create all the lists that we need
figure_attribution_list = []

count = 0
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

    for fig_attribution in xml.findall('.//attribution'):  # find all the attributions
        count += 1
        print count
        if fig_attribution != None:
            fig_attribution_title = fig_attribution.find('.//title')
            if fig_attribution_title != None:
                fig_attribution_text = fig_attribution_title.text
            else:
                fig_attribution_text = 'No title'
            fig_attribution_author = fig_attribution.find('.//author')
            if fig_attribution_author != None:
                try:
                    fig_attribution_text = fig_attribution_text + ' by {}'.format(fig_attribution_author.text)
                except:
                    continue
            else:
                fig_attribution_text = fig_attribution_text + ' by anonymous'
            fig_attribution_licence = fig_attribution.find('.//licence')
            if fig_attribution_licence != None:
                fig_attribution_text = fig_attribution_text + ' under {} licence'.format(fig_attribution_licence.text)
            else:
                fig_attribution_text = fig_attribution_text + ' under unknown licence'
            fig_attribution_url = fig_attribution.find('.//url')
            if fig_attribution_url != None:
                fig_attribution_text = fig_attribution_text + ' at {}'.format(fig_attribution_url.text)
            else:
                fig_attribution_text = fig_attribution_text + ''
            figure_attribution_list.append(fig_attribution_text)

#figure_attribution_list.sort()

# write the contents of each dictionary and list to a file
with open('gr10-lifescience-attributions', 'w') as file:
    file.write(str(figure_attribution_list))
