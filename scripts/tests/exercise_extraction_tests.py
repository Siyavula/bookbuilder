from unittest import TestCase

import os
from lxml import etree

from extract_exercises import ExerciseExtractor


class ExerciseExtractorTests(TestCase):
    def setUp(self):
        self.path = '/home/heather/Desktop/books/bookbuilder/scripts/tests/sample-files-for-testing/exercise-files/full-files'
        self.file_list = os.listdir(self.path)
        self.file_list.sort()
        self.exercises = ExerciseExtractor(self.path)
        self.expected_dict_keys = [
            '01-ideal-file',
            '02-perfect-file'
        ]
        self.expected_file_list = [
            '/home/heather/Desktop/books/bookbuilder/scripts/tests/sample-files-for-testing/exercise-files/solution-files/01-ideal-file.solutions.cnxmlplus.html',
            '/home/heather/Desktop/books/bookbuilder/scripts/tests/sample-files-for-testing/exercise-files/solution-files/02-perfect-file.solutions.cnxmlplus.html'
        ]

    def test_exercise_file_list(self):
        self.exercises.create_exercises_file(False)
        assert self.exercises.solutions.keys() == self.expected_dict_keys
    
    def test_exercise_file_contents(self):
        contents_expected = ''
        contents_actual = ''
        for file_name in self.expected_file_list:
            with open(file_name, 'r') as file:
                contents_expected += file.read()
        self.exercises.create_exercises_file(False)
        for key in self.exercises.solutions.keys():
            contents_actual += self.exercises.solutions[key]
        assert contents_expected == contents_actual
