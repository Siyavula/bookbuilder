'''This module contains the book class. It is a high level class that
handles caching, validation and convertion of cnxmlplus files'''

import os
import logging
import ast

from chapter import chapter as _chapter
from utils import mkdir_p


class Book(object):

    ''' Class to represent a whole book
    '''

    def __init__(self):
        self.repo_folder = os.path.abspath(os.curdir)
        self.build_folder = os.path.join(self.repo_folder, 'build')

        self.chapters = []
        # Read the cache and update the cache_object
        self.cache_object = self.read_cache()

        # If the object is empty, then we need to go and discover the chapters
        self._discover_chapters(self.cache_object)

    def _discover_chapters(self, cache_object):
        ''' Add all the .cnxmlplus files in the current folder'''

        files = os.listdir(os.curdir)
        cnxmlplusfiles = [
            f for f in files if f.strip().endswith('.cnxmlplus')]
        if len(cnxmlplusfiles) < 1:
            logging.warn("No cnxmlplus files found in current folder")

        cnxmlplusfiles.sort()

        for cfile in cnxmlplusfiles:
            # see if this chapter occurs in the cache_object
            if cfile in cache_object['chapters'].keys():
                # pass the previous hash to the chapter initialisation method
                previous_hash = cache_object['chapters'][cfile]['hash']
                previous_validation_status = cache_object[
                    'chapters'][cfile]['previous_validation_status']
                previous_render_problems = cache_object[
                    'chapters'][cfile]['render_problems']

                thischapter = _chapter(cfile, hash=previous_hash,
                                       valid=previous_validation_status,
                                       render_problems=previous_render_problems)
            else:
                # pass the prev has has None so that validation is forced
                thischapter = _chapter(cfile, hash=None, render_problems=False)

                # this chapter was not in the cache_object, add an empty dict
                # for it
                cache_object['chapters'][cfile] = {}

            # now update the cache_object
            cache_object['chapters'][cfile]['hash'] = thischapter.hash
            cache_object['chapters'][cfile][
                'previous_validation_status'] = thischapter.valid
            self.chapters.append(thischapter)

        self.write_cache()

    def show_status(self):
        ''' Print a listing of the chapters in book
        '''
        print("\nCh.  Valid     File\n" + '-' * 79)
        for chapter in self.chapters:
            print(chapter.info())
        print('-' * 79)

    def read_cache(self):
        ''' Read cache object inside the .bookbuilder/cache_object.txt

        Returns:
            None if cache_object.txt doesn't exist
            cache_object of type dict if it does

        '''

        # check whether .bookbuilder folder exists
        # and initialise it if it doesn't
        if not os.path.exists('.bookbuilder'):
            print("Creating .bookbuilder folder")
            mkdir_p('.bookbuilder')

        cache_object_path = os.path.join('.bookbuilder', 'cache_object.txt')

        if not os.path.exists(cache_object_path):
            # create one if it doesn't exist
            cache_object = self.create_cache_object()

            return cache_object
        else:
            with open(cache_object_path, 'r') as cop:
                copcontent = cop.read()
                if len(copcontent) == 0:
                    cache_object = self.create_cache_object()
                else:
                    cache_object = ast.literal_eval(copcontent)

                return cache_object

    def write_cache(self):
        ''' write cache object to the .bookbuilder folder

        '''
        cache_object_path = os.path.join('.bookbuilder', 'cache_object.txt')

        with open(cache_object_path, 'w') as cop:
            cop.write(self.cache_object.__str__())

    def create_cache_object(self):
        ''' create an empty cache_object dictionary
        '''
        # make it a dict
        cache_object = {}

        # create a key for chapters
        cache_object['title'] = None
        cache_object['chapters'] = {}

        return cache_object

    def convert(self, formats=None, parallel=True):
        ''' Convert all the chapters to the given output formats.

        Default output format is both tex and html
        '''
        if formats is None:
            formats = ['tex', 'html', 'xhtml', 'mobile']

        for chapter in self.chapters:
            # find this chapter's attributes from the cache dictionary
            chapter.convert(self.build_folder, formats, parallel=parallel)

            # The chapter may not have converted all the images correctly.
            # Set a flag in the cache_object
            self.cache_object['chapters'][chapter.file]['render_problems'] = chapter.render_problems
