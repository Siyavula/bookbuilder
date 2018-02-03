import os
import errno
import shutil
import multiprocessing
from lxml import etree


def mkdir_p(path):
    '''mkdir -p functionality

    from:
    http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    '''
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def copy_if_newer(src, dest):
    ''' Copy a file from src to  dest if src is newer than dest

    Returns True if success or False if there was a problem
    '''
    success = True
    dest_dir = os.path.dirname(dest)
    if (dest_dir is None) or (src is None):
        success = False
        return success
    if not os.path.exists(dest_dir):
        mkdir_p(dest_dir)

    if os.path.exists(src):
        # check whether src was modified more than a second after dest
        # and only copy if that was the case
        srcmtime = os.path.getmtime(src)
        try:
            destmtime = os.path.getmtime(dest)
            if srcmtime - destmtime > 1:
                shutil.copy2(src, dest)

        except OSError:
            # destination doesn't exist
            shutil.copy2(src, dest)
    else:
        success = False

    return success


def Map(function, data, parallel=True):
    ''' Runs parallel or serial map given a function and data
        mode can be one of 'serial' or 'parallel'
    '''

    if not parallel:
        result = map(function, data)
    else:
        pool = multiprocessing.Pool(multiprocessing.cpu_count()-1)
        result = pool.map(function, data)
        pool.close()
        pool.join()

    return result


class TOCBuilder(object):
    ''' Class for TOC'''

    def __init__(self):
        self.entries = []
        self.previous_element = None

    def as_etree_element(self):
        ''' Returns Toc as etree element'''
        ol = etree.Element('ol')

        for entry in self.entries:
            if entry.as_etree_element():
                ol.append(entry.as_etree_element())

        return ol

    def add_entry(self, tocelement):
        ''' Add a new tocelement'''

        if tocelement.level > 2:
            return

        # if there are no entries
        if (not self.entries):
            self.entries.append(tocelement)
            self.previous_element = tocelement

            return

        if tocelement.level == 1:
            self.entries.append(tocelement)
            self.previous_element = tocelement

            return

        # if we add a lower level to a higher level
        if tocelement.level > self.previous_element.level:
            assert(tocelement.level - self.previous_element.level == 1)
            self.previous_element.children.append(tocelement)
            tocelement.parent = self.previous_element
            self.previous_element = tocelement

            return

        # we add a level the same as the previous one
        if tocelement.level == self.previous_element.level:
            self.previous_element.parent.children.append(tocelement)
            tocelement.parent = self.previous_element.parent
            self.previous_element = tocelement

            return

        # we add a higher than the previous one, could go from h3 to h1 or h3
        # to h2 etc.
        else:
            leveldiff = tocelement.level - self.previous_element.level
            parent = self.previous_element.parent
            for i in range(leveldiff + 1):
                parent = parent.parent

            parent.children.append(tocelement)
            tocelement.parent = parent
            self.previous_element = tocelement

            return


class TocElement(object):
    '''Class to represent an element in the TOC'''
    def __init__(self, filename, h_element):
        self.filename = filename
        self.element = h_element
        self.children = []
        self.parent = None
        self.level = int(self.element.tag[1])

    def as_etree_element(self):
        ''' Return object as etree element'''
        try:
            li = etree.Element('li')
            a = etree.Element('a')
            a.attrib['href'] = '{}#{}'.format(self.filename,
                                              self.element.attrib['id'])
            a.text = self.element.text
            li.append(a)
            ol = etree.Element('ol')
            for child in self.children:
                ol.append(child.as_etree_element())
            if len(ol) > 0:
                li.append(ol)

            return li
        except:
            # some items must not be in the toc
            return None


def add_unique_ids(html):
    ''' Given html etree object, return same object with unique ids for all the
    h1 and h2 titles'''

    IDs = []
    _id = 0
    headings = ['h1', 'h2']
    for heading in headings:
        for htag in html.findall('.//div/{}'.format(heading)):
            _class = htag.getparent().attrib.get('class')
            if _class not in ['chapter', 'section', 'exercises']:
                continue
            current_id = htag.attrib.get('id')
            if (current_id not in IDs) and (current_id is not None):
                IDs.append(current_id)
                continue

            # it doesn't have an ID
            new_id = "toc-id-{}".format(_id)
            while new_id in IDs:
                _id += 1
                new_id = "toc-id-{}".format(_id)
            IDs.append(new_id)
            htag.attrib['id'] = new_id
            _id += 1
        for htag in html.findall('.//section/{}'.format(heading)):
            _class = htag.getparent().attrib.get('class')
            if _class not in ['chapter', 'section', 'exercises']:
                continue
            current_id = htag.attrib.get('id')
            if (current_id not in IDs) and (current_id is not None):
                IDs.append(current_id)
                continue

            # it doesn't have an ID
            new_id = "toc-id-{}".format(_id)
            while new_id in IDs:
                _id += 1
                new_id = "toc-id-{}".format(_id)
            IDs.append(new_id)
            htag.attrib['id'] = new_id
            _id += 1
    return html


