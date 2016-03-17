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

    def test_book_structure_data(self):
        self.book_structure.create_structure(False)
        book_data = yaml.load(self.book_structure.book_data)
        with open('sample-files-for-testing/book_structure_test.yaml', 'r') as file:
            test_data = yaml.load(file)
        assert book_data == test_data
        