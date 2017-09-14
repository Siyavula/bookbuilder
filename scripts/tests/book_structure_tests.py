from unittest import TestCase

import os
from lxml import etree
import yaml

from create_book_structure import BookStructureCreation


class BookStructureTests(TestCase):
    def setUp(self):
        path = '/home/heather/Desktop/books/bookbuilder/scripts/tests/sample-files-for-testing/cnxmlplus_files'
        self.book_structure = BookStructureCreation(path)

    def test_book_structure_data(self):
        self.book_structure.create_structure(False)
        book_data = yaml.load(self.book_structure.book_data)
        test_data_path = '/home/heather/Desktop/books/bookbuilder/scripts/tests/sample-files-for-testing/book_structure_test.yaml'
        with open(test_data_path, 'r') as file:
            test_data = yaml.load(file)
        assert book_data== test_data