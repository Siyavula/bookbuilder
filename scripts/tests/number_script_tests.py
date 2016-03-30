from unittest import TestCase

import os
from lxml import etree

from number_html5 import NumberingClass


class NumberingClassTests(TestCase):
    def setUp(self):
        path = '/home/heather/Desktop/books/bookbuilder/scripts/tests/sample-files-for-testing/unnumbered_files'
        self.number_class = NumberingClass(path)

    def test_number_files(self):
        self.number_class.number_files(False)
        correct_file_names = [
            '01-ideal-file-00.cnxmlplus.html', 
            '01-ideal-file-01.cnxmlplus.html', 
            '02-perfect-file-00.cnxmlplus.html'
            ]
        for correct_file_name in correct_file_names:
            full_unumbered_file_name = '{}/{}'.format('/home/heather/Desktop/books/bookbuilder/scripts/tests/sample-files-for-testing/unnumbered_files', correct_file_name)
            full_numbered_file_name = '{}/{}'.format('/home/heather/Desktop/books/bookbuilder/scripts/tests/sample-files-for-testing/numbered_files', correct_file_name)
            assert self.number_class.numbered_files[full_unumbered_file_name] == etree.tostring(etree.parse(full_numbered_file_name, etree.HTMLParser()), pretty_print=True)
