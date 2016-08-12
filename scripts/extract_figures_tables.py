'''
This code does the following three things:
1. Extracts the figure references and makes a dictionary of these referenced by the appropriate figure number
2. Extracts the table references and makes a dictionary of these referenced by the appropriate table number
3. Extracts the figure attributions and puts them in a list along with the figure number
'''
import os
from lxml import etree

path = '/home/heather/Desktop/books/physical-sciences-11/english'

# create all the lists and dictionaries that we need
figure_dictionary = {}
table_dictionary = {}
figure_attribution_list = []

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
    figure_counter = 1  # start a figure counter running
    table_counter = 1  # start a table counter running
    
    for figure in xml.findall('.//figure'):  # find all the figures
        figure_type = figure.find('.//type')  # get the type of the figure
        fig_attribution = figure.find('.//attribution')  # extract the attribution if it exists
        try:
            figure_id = figure.attrib['id']  # get the id
            figure_id = '#{}'.format(figure_id)
        except:
            continue
        if figure_type.text == 'figure':
            figure_number = '{}.{}'.format(chapter_number, figure_counter)  # make the number
            if fig_attribution != None:
                fig_attribution_title = fig_attribution.find('.//title')
                if fig_attribution_title != None:
                    fig_attribution_text = fig_attribution_title.text
                else:
                    fig_attribution_text = 'No title'
                fig_attribution_author = fig_attribution.find('.//author')
                if fig_attribution_author != None:
                    fig_attribution_text = fig_attribution_text + ' by {}'.format(fig_attribution_author.text)
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
                figure_dictionary[figure_id] = '{}'.format(figure_number)  # create a dictionary key-value pair
                fig_attribution_text = '{}: {}'.format(figure_number, fig_attribution_text)
                figure_attribution_list.append(fig_attribution_text)
                figure_counter += 1  # increment the figure counter
        elif figure_type.text == 'table':
            table_number = '{}.{}'.format(chapter_number, table_counter)
            table_dictionary[figure_id] = '{}'.format(table_number)
            table_counter += 1
figure_attribution_list.sort()

# write the contents of each dictionary and list to a file
with open('gr11-science-fig_refs.txt', 'w') as file:
    #file.write(str(figure_dictionary))
    #file.write('\n')
    #file.write(str(table_dictionary))
    file.write('\n')
    file.write(str(figure_attribution_list))
