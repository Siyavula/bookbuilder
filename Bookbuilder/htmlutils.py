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


def add_mathjax(html):
    ''' Given html as string, insert a <script> tag that will include mathjax
    from a local folder called 'mathjax'

    Return as string

    '''

    html = etree.HTML(html)
    head = html.find('.//head')
    script = etree.fromstring(r'''<script type="text/javascript"
  src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>''')
    head.append(script)
    html = etree.tostring(html, method='xml')

    return html


def repair_equations(html):
    ''' Some equations contain escaped unicode entities. Replace them with unicode.

    '''

    unicode_to_replace = ((r'&amp;#183;', r'&#183;'),
                          (r'&amp;#160;', r' '),
                          (r'&amp;#8451;', r'$^\circ$'),
                          (')~\\', ') \\'))
    for un in unicode_to_replace:
        html = html.replace(un[0], un[1])

    return html
