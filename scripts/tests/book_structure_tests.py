from unittest import TestCase

import os
from lxml import etree
import yaml

from create_book_structure import BookStructureCreation


class BookStructureTests(TestCase):
    def setUp(self):
        path = '/home/heather/Desktop/books/bookbuilder/scripts/tests/sample-files-for-testing/unnumbered_files'
        file_list = os.listdir(path)
        file_list.sort()
        self.book_structure = BookStructureCreation(file_list)

    def test_structure_file(self):
        assert 'Perfect chapter' in self.book_structure.section_chapter_extract()
        