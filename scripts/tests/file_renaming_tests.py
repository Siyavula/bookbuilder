from unittest import TestCase

import os

from rename_files import FileRenamer


class FileRenamerTests(TestCase):
    def setUp(self):
        path = '/home/heather/Desktop/books/bookbuilder/scripts/tests/sample-files-for-testing/numbered_files'
        self.file_renamer = FileRenamer(path)

    def test_file_renamed(self):
        file_list = self.file_renamer.rename_all_files(False)
        correct_file_names = [
            '01-ideal-file-01.cnxmlplus.html', 
            '01-ideal-file-02.cnxmlplus.html', 
            '02-perfect-file-01.cnxmlplus.html'
            ]
        assert len(correct_file_names) == len(file_list)
        for i in range(len(correct_file_names)):
            assert correct_file_names[i] == file_list[i]
