#!/usr/bin/env python
from distutils.core import setup
#from distutils.extension import Extension
#from Cython.Distutils import build_ext

import sys

for cmd in ('egg_info', 'develop'):
    if cmd in sys.argv:
        from setuptools import setup

def get_version():
    with open("pymorphy2/version.py", "rt") as f:
        return f.readline().split("=")[1].strip(' "')

setup(
    name = 'pymorphy2',
    version = get_version(),
    author = 'Mikhail Korobov',
    author_email = 'kmike84@gmail.com',
    url = 'https://github.com/kmike/pymorphy2/',

    description = 'Morphological analyzer (POS tagger + inflection engine) for Russian language.',
    long_description = open('README.rst').read() + open('docs/CHANGES.rst').read(),

    license = 'MIT license',
    packages = ['pymorphy2', 'pymorphy2.vendor'],
    scripts=['bin/pymorphy'],
    requires=['dawg_python (>= 0.5)'],

#    cmdclass = {'build_ext': build_ext},
#    ext_modules = [Extension("pymorphy2.tagger", ["pymorphy2/tagger.py"])],

    classifiers=[
          'Development Status :: 1 - Planning',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: Russian',
          'Natural Language :: English',
          'Natural Language :: German',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Text Processing :: Linguistic',
    ],
)
