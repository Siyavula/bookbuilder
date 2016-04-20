"""
Usage:
    extract_exercises.py <path_name>

Options:
    path_name gives the path to the files that need to be numbered

Examples:
    extract_exercises.py '/home/books/grade-10-mathslit-latex/english'

"""
import os
import sys
from docopt import docopt
from lxml import etree

class ExerciseExtractor():
    """
    This class extracts the exercises from html files and writes them out
    to the appropriate solutions file
    """
    def __init__(self, path):
        self.path = path
        self.file_list = os.listdir(self.path)
        self.file_list.sort()
        self.exercise_contents = ''
        self.exercise_contents_dict = {}
    
    def create_exercises_file(self, write_back_to_file_boolean=False):
        self.solutions = self.extract_exercises(self.file_list, self.path)
        if not write_back_to_file_boolean:
            return
        
        for file_name in self.solutions.keys():
            self.write_to_solutions_file(self.solutions[file_name], file_name)
    
    def extract_exercises(self, file_list, path):
        for file_name in self.file_list:
            full_file_name = '{}/{}'.format(self.path, file_name)

            # Skip directories
            if os.path.isdir(full_file_name):
                continue

            # we need to remove files that do not contain xml
            # and files that do not start with a number
            if not file_name.endswith('.cnxmlplus.html'):
                continue
            if not file_name[0].isdigit():
                continue

            xml = etree.parse(full_file_name, etree.HTMLParser())
            
            for div in xml.findall('.//div[@class]'):
                if div.attrib['class'] == 'section':
                    if div.find('.//div') is not None:
                        problemset = div.find('.//div')
                        if problemset.attrib['class'] == 'problemset':
                            exercise_div = etree.Element('div')
                            exercise_div.set('class', 'section')
                            exercise_div.append(problemset)
                            self.exercise_contents += etree.tostring(exercise_div, pretty_print=True)

            if self.file_list.index(file_name) != len(self.file_list) - 1:
                index = self.file_list.index(file_name)
                if file_name.split('.')[0][:-3] != self.file_list[index + 1].split('.')[0][:-3]:
                    self.exercise_contents_dict[file_name.split('.')[0][:-3]] = self.exercise_contents
                    self.exercise_contents = ''
                else:
                    continue
            else:
                self.exercise_contents_dict[file_name.split('.')[0][:-3]] = self.exercise_contents
        return self.exercise_contents_dict

    def write_to_solutions_file(self, file_contents, file_name):
        with open(file_name, 'w') as file:
            file.write(file_contents)

if __name__ == "__main__":
    path = docopt(__doc__)['<path_name>']
    exercises = ExerciseExtractor(path)
    exercises.create_exercises_file(True)
