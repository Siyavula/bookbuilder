from lxml import etree


def xhtml_cleanup(xhtmlstr):
    ''' Given xhtmlstr input, parse it as xml and make some fixes to it for
    inclusion into an epub, validated by Epubcheck 3.01

    '''

    xhtml = etree.HTML(xhtmlstr)

    # Fix ID with colons in them
    IDs = []
    for element in xhtml.iter():
        ID = element.attrib.get('id')
        if ID:
            if ID not in IDs:
                IDs.append(ID)
            else:
                i = 1
                newID = ID.strip() + '-' + str(i)
                while newID in IDs:
                    i += 1
                    newID = ID.strip() + '-' + str(i)

                element.attrib['id'] = newID
                IDs.append(newID)

            # replace it with something valid
            element.attrib['id'] = element.attrib['id'].replace(':', '-')

    for figure in xhtml.findall('.//figure'):
        figure.tag = 'div'
        figure.attrib['class'] = 'figure'
        for figcaption in figure.findall('.//figcaption'):
            figcaption.tag = 'div'
            figcaption.attrib['class'] = 'figcaption'


    for table in xhtml.findall('.//table'):
        if 'summary' in table.attrib.keys():
            del table.attrib['summary']

    xhtmlstr = etree.tostring(xhtml, xml_declaration=True, encoding='utf-8')
    xhtmlstr = xhtmlstr.replace('<html>', '<html\
 xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">')

    return xhtmlstr
