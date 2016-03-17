from unittest import TestCase

import os
from lxml import etree
import yaml

from create_book_structure import BookStructureCreation


class BookStructureTests(TestCase):
    def setUp(self):
        path = '/home/heather/Desktop/books/bookbuilder/scripts/tests/sample-files-for-testing/cnxmlplus_files'
        file_list = os.listdir(path)
        file_list.sort()
        self.book_structure = BookStructureCreation(file_list, path)

    def test_structure_file(self):
        self.book_structure.create_structure(False)
        assert 'This is the first chapter' in self.book_structure.book_data
        assert 'Section the first, in chapter the third' in self.book_structure.book_data
        assert 'Subsection the first, in chapter the second' not in self.book_structure.book_data
        