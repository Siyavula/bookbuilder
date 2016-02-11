from unittest import TestCase

import os


from number_html5 import NumberingClass


class NumberingClassTests(TestCase):
    def setUp(self):
        path = '/home/heather/Desktop/books/scripts/tests/sample-files-for-testing/unnumbered_files'
        file_list = os.listdir(path)
        file_list.sort()
        self.number_class = NumberingClass(file_list)

    def test_number_files(self):
        self.number_class.number_files(False)
        correct_file_names = [
            '01-ideal-file-00.cnxmlplus.html', 
            '01-ideal-file-01.cnxmlplus.html', 
            '02-perfect-file-00.cnxmlplus.html']
        for correct_file_name in correct_file_names:
            full_file_name = '{}/{}'.format('/home/heather/Desktop/books/scripts/tests/sample-files-for-testing/unnumbered_files', correct_file_name)
            correct_file = open(full_file_name, 'r')
            import ipdb; ipdb.set_trace()
            assert self.number_class.numbered_files[full_file_name] == correct_file
    
#class GeneralCounterTests(TestCase):
    #def sanity_test(self):
        #'''
        #The main purpose here is to ensure that we always get xml out, not None
        #'''
        #assert number_class.xml != None
    
    #def test_file_number_correct_range(self):
        #'''
        #We expect the file_number to be an int in range(0,25)
        #Currently our books have at most 23 chapters so upper limit is less than 25
        #We expect the file_counter to be an int in range(0,15)
        #Currently our books do not contain very long chapters with many
        #subsections in them so the upper limit is less than 15
        #'''
        #assert type(number_class.file_number) == int
        #assert type(number_class.file_counter) == int
        #assert number_class.file_number in range(0,25)
        #assert number_class.file_counter in range(0,15)
    
    #def test_chapter_numbering(self):
        #'''
        #This should correctly insert the chapter number (which is the file_number)
        #into the xml
        #'''
        #try:
            #assert number_class.chapter_number_insert(number_class.file_number).find(number_class.file_number) != -1
        #except AttributeError:
            #pass
    
    #def test_section_numbering(self):
        #'''Test that the section numbering is correctly added to the xml
        #'''
        #assert '{}.{}'.format(number_class.file_number, number_class.section_number) in number_class.section_number_insert(number_class.file_number, number_class.section_number)
    
    #def test_exercise_numbering(self):
        #'''Test that the exercise numbering is correctly added to the xml
        #'''
        #assert '{}.{}'.format(number_class.file_number, number_class.exercise_number) in number_class.exercise_number_insert(number_class.file_number, number_class.exercise_number)
    
    #def test_worked_example_numbering(self):
        #'''Test that the worked example numbering is correctly added to the xml
        #'''
        #assert '{}.{}'.format(number_class.file_number, number_class.worked_example_number) in number_class.worked_example_number_insert(number_class.file_number, number_class.worked_example_number)
    
    #def test_table_numbering(self):
        #'''
        #Tests that tables are numbered correctly in the format 
        #chapter_number.table_number
        #table_number should be of type int
        #Check that the counter resets when the file_counter resets
        #'''
        #assert '{}.{}'.format(number_class.file_number, number_class.table_counter) in number_class.table_number_insert(number_class.file_number, number_class.table_number)
        #assert type(number_class.table_counter) == int
        #if number_class.file_counter == 0:
            #assert number_class.table_counter == 1
        #else:
            #assert number_class.table_counter != 1
            #assert number_class.table_counter != 0
    
    #def test_figure_numbering(self):
        #'''
        #Tests that figures are numbered correctly in the format 
        #chapter_number.figure_number
        #figure_number should be of type int
        #Check that the counter resets when the file_counter resets
        #'''
        #try:
            #assert '{}.{}'.format(number_class.file_number, number_class.figure_number) in number_class.figure_number_insert(number_class.file_number, number_class.figure_number)
            #assert type(number_class.figure_number) == int
            #if number_class.file_counter == 0:
                #assert number_class.figure_number == 1
            #else:
                #assert number_class.figure_number != 1
                #assert number_class.figure_number != 0
        #except TypeError:
            #pass

#class TextAdditionClass(TestCase):
    #def test_chapter_text(self):
        #'''
        #This tests that the word Chapter is inserted into the chapter heading
        #'''
        #assert 'Chapter' in number_class.chapter_number_insert(number_class.file_number)
    
    #def test_figure_text(self):
        #'''
        #This tests that the word Figure is inserted into the figure caption
        #This also tests that the figure caption does not contain the word None
        #'''
        #assert 'Figure' in number_class.figure_number_insert(number_class.file_number, number_class.figure_number)
        #assert 'None' not in number_class.figure_number_insert(number_class.file_number, number_class.figure_number)
    
    #def test_table_text(self):
        #'''
        #This tests that the word Table is inserted into the table caption
        #This also tests that the table caption does not contain the word None
        #'''
        #assert 'Table' in number_class.table_number_insert(number_class.file_number, number_class.table_number)
        #assert 'None' not in number_class.table_number_insert(number_class.file_number, number_class.table_number)
    
    #def test_hyperlink_text(self):
        #'''
        #This tests that the hyperlinks for figures and tables are properly inserted
        #'''
        #assert 'fig:' not in number_class.hyperlink_text_fix(number_class.figure_dictionary, number_class.table_dictionary)
        #assert 'tab:' not in number_class.hyperlink_text_fix(figure_dictionary, table_dictionary)
        #assert 'Figure ' in number_class.hyperlink_text_fix(number_class.figure_dictionary, number_class.table_dictionary)
        #assert 'Table ' in number_class.hyperlink_text_fix(number_class.figure_dictionary, number_class.table_dictionary)
    
    #def test_section_text(self):
        #'''
        #This tests that the section text contains a span with shortcode
        #'''
        #assert '<span class="shortcode">' in number_class.section_number_insert(number_class.file_number, number_class.section_number)
    
    #def test_subsection_text(self):
        #'''
        #This tests that the subsection text contains a span with shortcode
        #'''
        #assert '<span class="shortcode">' in number_class.subsection_number_insert(number_class.subsection_number)
    
    #def test_worked_example_text(self):
        #'''
        #This tests that the worked example text contains the text Worked Example
        #'''
        #assert 'Worked Example ' in number_class.worked_example_number_insert(number_class.file_number, number_class.worked_example_number)
    
    #def test_exercise_text(self):
        #'''
        #This tests that the worked example text contains the text Worked Example
        #'''
        #assert 'Exercise ' in number_class.exercise_number_insert(number_class.file_number, number_class.exericise_number)
        #assert '<span class="ExerciseTitle">' in number_class.exercise_number_insert(number_class.file_number, number_class.exercise_number)
