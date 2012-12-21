# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function, division

import logging
import time
import sys
import pprint
import codecs

import pymorphy2
from pymorphy2 import opencorpora_dict, test_suite_generator
from pymorphy2.vendor.docopt import docopt
from pymorphy2.os_utils import download_bz2, get_mem_usage

logger = logging.getLogger('pymorphy2')
logger.addHandler(logging.StreamHandler())

XML_BZ2_URL = "http://opencorpora.org/files/export/dict/dict.opcorpora.xml.bz2"

# ============================ Commands ===========================

def compile_dict(in_filename, out_folder=None, overwrite=False, prediction_options=None):
    """
    Make a Pymorphy2 dictionary from OpenCorpora .xml dictionary.
    """
    if out_folder is None:
        out_folder = 'dict'
    opencorpora_dict.to_pymorphy2_format(in_filename, out_folder, overwrite, prediction_options=prediction_options)

def xml_to_json(in_filename, out_filename):
    """
    Parse XML and caches result to json.
    """
    opencorpora_dict.xml_dict_to_json(in_filename, out_filename)


def show_dict_mem_usage(dict_path, verbose=False):
    """
    Show dictionary memory usage.
    """
    initial_mem = get_mem_usage()
    initial_time = time.time()

    dct = opencorpora_dict.load(dict_path)

    end_time = time.time()
    mem_usage = get_mem_usage()

    logger.info('Memory usage: %0.1fM dictionary, %0.1fM total (load time %0.2fs)',
        (mem_usage-initial_mem)/(1024*1024), mem_usage/(1024*1024), end_time-initial_time)

    if verbose:
        try:
            from guppy import hpy; hp=hpy()
            logger.debug(hp.heap())
        except ImportError:
            logger.warn('guppy is not installed, detailed info is not available')


def show_dict_meta(dict_path):
    dct = opencorpora_dict.load(dict_path)
    for key, value in dct.meta.items():
        logger.info("%s: %s", key, value)


def make_test_suite(dict_filename, out_filename, word_limit=100):
    """
    Make a test suite from (unparsed) OpenCorpora dictionary.
    """
    return test_suite_generator.make_test_suite(
        dict_filename, out_filename, word_limit=int(word_limit))


def download_xml(out_filename, verbose):
    """
    Download an updated XML from OpenCorpora
    """
    def on_chunk():
        if verbose:
            sys.stdout.write('.')
            sys.stdout.flush()

    logger.info('Creating %s from %s' % (out_filename, XML_BZ2_URL))
    with open(out_filename, "wb") as f:
        download_bz2(XML_BZ2_URL, f, on_chunk=on_chunk)

    logger.info('\nDone.')


def _parse(dict_path, in_filename, out_filename):
    from pymorphy2 import tagger
    morph = pymorphy2.tagger.Morph.load(dict_path)

    with codecs.open(in_filename, 'r', 'utf8') as in_file:
        with codecs.open(out_filename, 'w', 'utf8') as out_file:
            for line in in_file:
                word = line.strip()
                parses = morph.parse(word)
                parse_str = "|".join([p[1] for p in parses])
                out_file.write(word + ": " +parse_str + "\n")


# =============================================================================

DOC ="""

Pymorphy2 is a Russian POS tagger and inflection engine.

Usage:
    pymorphy dict compile <IN_FILE> [--out <PATH>] [--force] [--verbose] [--max_forms_per_class <NUM>] [--min_ending_freq <NUM>] [--min_paradigm_popularity <NUM>]
    pymorphy dict xml2json <IN_XML_FILE> <OUT_JSON_FILE> [--verbose]
    pymorphy dict download [--verbose]
    pymorphy dict download_xml <OUT_FILE> [--verbose]
    pymorphy dict mem_usage [--dict <PATH>] [--verbose]
    pymorphy dict make_test_suite <IN_FILE> <OUT_FILE> [--limit <NUM>] [--verbose]
    pymorphy dict meta [--dict <PATH>]
    pymorphy _parse <IN_FILE> <OUT_FILE> [--dict <PATH>] [--verbose]
    pymorphy -h | --help
    pymorphy --version

Options:
    -v --verbose                        Be more verbose
    -f --force                          Overwrite target folder
    -o --out <PATH>                     Output folder name [default: dict]
    --limit <NUM>                       Min. number of words per gram. tag [default: 100]
    --min_ending_freq <NUM>             Prediction: min. number of suffix occurances [default: 2]
    --min_paradigm_popularity <NUM>     Prediction: min. number of lemmas for the paradigm [default: 3]
    --max_forms_per_class <NUM>         Prediction: max. number of word forms per part of speech [default: 1]
    --dict <PATH>                       Dictionary folder path [default: dict]

"""

def main():
    """
    Pymorphy CLI interface dispatcher
    """
    args = docopt(DOC, version=pymorphy2.__version__)

    if args['--verbose']:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if args['_parse']:
        return _parse(args['--dict'], args['<IN_FILE>'], args['<OUT_FILE>'])

    elif args['dict']:
        if args['compile']:
            prediction_options = dict(
                (key, int(args['--'+key]))
                for key in ('max_forms_per_class', 'min_ending_freq', 'min_paradigm_popularity')
            )
            return compile_dict(args['<IN_FILE>'], args['--out'], args['--force'], prediction_options)
        elif args['xml2json']:
            return xml_to_json(args['<IN_XML_FILE>'], args['<OUT_JSON_FILE>'])
        elif args['mem_usage']:
            return show_dict_mem_usage(args['--dict'] or 'dict', args['--verbose'])
        elif args['meta']:
            return show_dict_meta(args['--dict'] or 'dict')
        elif args['make_test_suite']:
            return make_test_suite(args['<IN_FILE>'], args['<OUT_FILE>'], int(args['--limit']))
        elif args['download_xml']:
            return download_xml(args['<OUT_FILE>'], args['--verbose'])
        elif args['download']:
            raise NotImplementedError()

    logger.debug(args)
