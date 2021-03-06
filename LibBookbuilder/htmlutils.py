''' Miscellaneous functions that deals with html processing

'''
from lxml import etree
import HTMLParser
import re


def xhtml_cleanup(xhtmlstr):
    ''' Given xhtmlstr input, parse it as xml and make some fixes to it for
    inclusion into an epub, validated by Epubcheck 3.01

    '''

    xhtml = etree.HTML(xhtmlstr)

    # Fix ID with colons in them
    _ids = []
    for element in xhtml.iter():
        _id = element.attrib.get('id')
        if _id:
            if _id not in _ids:
                _ids.append(_id)
            else:
                i = 1
                new_id = _id.strip() + '-' + str(i)
                while new_id in _ids:
                    i += 1
                    new_id = _id.strip() + '-' + str(i)

                element.attrib['id'] = new_id
                _ids.append(new_id)

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

    for exercise in xhtml.findall('.//div[@class="exercises"]'):
        exercise.attrib['class'] = 'section'
        firstchild = exercise[0]
        if firstchild.tag.startswith('h'):
            firstchild.tag = 'h2'
            firstchild.text = 'Exercises'

    xhtmlstr = etree.tostring(xhtml, encoding='utf-8')
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
    r''' Some equations contain escaped unicode entities. Replace them with
    unicode.

    Some images have nested math environments i.e. $\(\text{blah}\)$, remove
    the inner math delimiters

    '''
    htmlparser = HTMLParser.HTMLParser()
    html = html.replace('&amp;#', '&#')
    entities = re.findall('&#.*?;', html)
    for ent in entities:
        html = html.replace(ent, htmlparser.unescape(ent))

    # some unicode needs to get replaced with math-mode symbols but they cannot
    # use those symbols if they are already in a math mode.
    return html
