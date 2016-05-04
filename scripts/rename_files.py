"""
Usage:
    rename_files.py <path_name>

Options:
    path_name gives the path to the files that need to be renamed

Examples:
    rename_files.py '/home/books/grade-10-mathslit-latex/english'

"""
import os
import sys
from docopt import docopt


class FileRenamer():
    """
    This class extracts the file list and renames all the files
    in the file list
    """
    def __init__(self, path):
        self.path = path
        self.file_list = os.listdir(self.path)
        self.file_list.sort()
        self.new_file_list = []
        self.temp_file_list = []

    def rename_all_files(self, rename_file_boolean=False):
        self.file_renamer(self.file_list, self.path)
        if not rename_file_boolean:
            return self.new_file_list
        else:
            for i in range(len(self.temp_file_list)):
                #import ipdb; ipdb.set_trace()
                full_file_name_old = '{}/{}'.format(self.path, self.file_list[i])
                full_file_name_temp = '{}/{}'.format(self.path, self.temp_file_list[i])
                full_file_name_new = '{}/{}'.format(self.path, self.new_file_list[i])
                os.rename(full_file_name_old, full_file_name_temp)
            for i in range(len(self.new_file_list)):
                full_file_name_temp = '{}/{}'.format(self.path, self.temp_file_list[i])
                full_file_name_new = '{}/{}'.format(self.path, self.new_file_list[i])
                os.rename(full_file_name_temp, full_file_name_new)

    def file_renamer(self, file_list, path):
        for file_name in file_list:
            full_file_name = '{}/{}'.format(self.path, file_name)

            # Skip directories
            if os.path.isdir(full_file_name):
                continue

            # we need to remove files that do not contain xml
            # and files that do not start with a number
            if not file_name.endswith('html'):
                continue
            if not file_name[0].isdigit():
                continue
            
            file_name_no_prefix = file_name.split('.')
            file_number_int = int(file_name_no_prefix[0].split('-')[-1])
            file_number_int += 1
            if file_number_int < 10:
                file_number_string = '0{}'.format(file_number_int)
            else:
                file_number_string = str(file_number_int)
            partial_new_file_name = file_name_no_prefix[0].split('-')[:-1]
            new_file_name = '{}-{}.cnxmlplus.html'.format('-'.join(partial_new_file_name), file_number_string)
            temp_file_name = '{}-{}temp.cnxmlplus.html'.format('-'.join(partial_new_file_name), file_number_string)
            self.new_file_list.append(new_file_name)
            self.temp_file_list.append(temp_file_name)
            

        return (self.new_file_list, self.temp_file_list)

if __name__ == "__main__":
    path = docopt(__doc__)['<path_name>']
    renamed_files = FileRenamer(path)
    renamed_files.rename_all_files(True)
