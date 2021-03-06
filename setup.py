#!/usr/bin/env python

from setuptools import setup

setup(name='Bookbuilder',
      version='0.3',
      description='Tools for generating Siyavula\'s publishing formats',
      author='Ewald Zietsman',
      author_email='ewald@siyavula.com',
      url='http://www.siyavula.com/',
      packages=['LibBookbuilder'],
      scripts=['bookbuilder'],
      install_requires=['docopt',
                        'lxml',
                        'termcolor',],
      )
