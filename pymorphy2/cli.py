# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals, print_function, division

import logging
import time
import codecs

import pymorphy2
from pymorphy2.utils import get_mem_usage

logger = logging.getLogger('pymorphy2')


# ============================ Commands ===========================


def show_dict_mem_usage(dict_path=None, verbose=False):
    """
    Show dictionary memory usage.
    """
    initial_mem = get_mem_usage()
    initial_time = time.time()

    morph = pymorphy2.MorphAnalyzer(dict_path)

    end_time = time.time()
    mem_usage = get_mem_usage()

    logger.info(
        'Memory usage: %0.1fM dictionary, %0.1fM total (load time %0.2fs)',
        (mem_usage-initial_mem)/(1024*1024), mem_usage/(1024*1024), end_time-initial_time
    )

    if verbose:
        try:
            from guppy import hpy; hp=hpy()
            logger.debug(hp.heap())
        except ImportError:
            logger.warn('guppy is not installed, detailed info is not available')


def show_dict_meta(dict_path=None):
    morph = pymorphy2.MorphAnalyzer(dict_path)

    for key, value in morph.dictionary.meta.items():
        logger.info("%s: %s", key, value)


def _parse(dict_path, in_filename, out_filename):
    morph = pymorphy2.MorphAnalyzer(path=dict_path)
    with codecs.open(in_filename, 'r', 'utf8') as in_file:
        with codecs.open(out_filename, 'w', 'utf8') as out_file:
            for line in in_file:
                word = line.strip()
                parses = morph.parse(word)
                parse_str = "|".join([p[1] for p in parses])
                out_file.write(word + ": " +parse_str + "\n")


# =============================================================================

# Hacks are here to make docstring compatible with both
# docopt and sphinx.ext.autodoc.

head = """

Pymorphy2 is a morphological analyzer / inflection engine for Russian language.
"""
__doc__ = """
Usage::

    pymorphy dict meta [--dict <PATH>]
    pymorphy dict mem_usage [--dict <PATH>] [--verbose]
    pymorphy _parse <IN_FILE> <OUT_FILE> [--dict <PATH>] [--verbose]
    pymorphy -h | --help
    pymorphy --version

Options::

    --dict <PATH>       Dictionary folder path
    -v --verbose        Be more verbose
    -h --help           Show this help

"""
DOC = head + __doc__.replace('::\n', ':')


def main():
    """
    Pymorphy CLI interface dispatcher
    """
    logger.addHandler(logging.StreamHandler())

    from docopt import docopt
    args = docopt(DOC, version=pymorphy2.__version__)

    logger.setLevel(logging.DEBUG if args['--verbose'] else logging.INFO)
    logger.debug(args)

    if args['_parse']:
        return _parse(args['--dict'], args['<IN_FILE>'], args['<OUT_FILE>'])

    elif args['dict']:
        if args['mem_usage']:
            return show_dict_mem_usage(args['--dict'], args['--verbose'])
        elif args['meta']:
            return show_dict_meta(args['--dict'])
