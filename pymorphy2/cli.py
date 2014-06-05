# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function, division

import logging
import time
import sys
import codecs
import os

import pymorphy2
from pymorphy2 import opencorpora_dict, test_suite_generator
from pymorphy2.utils import download_bz2, get_mem_usage, json_read, json_write

logger = logging.getLogger('pymorphy2')
logger.addHandler(logging.StreamHandler())

XML_BZ2_URL = "http://opencorpora.org/files/export/dict/dict.opcorpora.xml.bz2"

# ============================ Commands ===========================

def compile_dict(in_filename, out_path=None, overwrite=False, prediction_options=None):
    """
    Make a Pymorphy2 dictionary from OpenCorpora .xml dictionary.
    """
    if out_path is None:
        out_path = 'dict'

    opencorpora_dict.convert_to_pymorphy2(
        opencorpora_dict_path = in_filename,
        out_path = out_path,
        overwrite = overwrite,
        prediction_options = prediction_options
    )

def show_dict_mem_usage(dict_path=None, verbose=False):
    """
    Show dictionary memory usage.
    """
    initial_mem = get_mem_usage()
    initial_time = time.time()

    morph = pymorphy2.MorphAnalyzer(dict_path)

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


def show_dict_meta(dict_path=None):
    morph = pymorphy2.MorphAnalyzer(dict_path)

    for key, value in morph.dictionary.meta.items():
        logger.info("%s: %s", key, value)


def make_test_suite(dict_filename, out_filename, word_limit=100):
    """ Make a test suite from (unparsed) OpenCorpora dictionary. """
    return test_suite_generator.make_test_suite(
        dict_filename, out_filename, word_limit=int(word_limit))


def download_dict_xml(out_filename, verbose):
    """ Download an updated dictionary XML from OpenCorpora """
    def on_chunk():
        if verbose:
            sys.stdout.write('.')
            sys.stdout.flush()

    logger.info('Creating %s from %s' % (out_filename, XML_BZ2_URL))
    with open(out_filename, "wb") as f:
        download_bz2(XML_BZ2_URL, f, on_chunk=on_chunk)

    logger.info('\nDone.')


def _parse(dict_path, in_filename, out_filename):
    morph = pymorphy2.MorphAnalyzer(dict_path)
    with codecs.open(in_filename, 'r', 'utf8') as in_file:
        with codecs.open(out_filename, 'w', 'utf8') as out_file:
            for line in in_file:
                word = line.strip()
                parses = morph.parse(word)
                parse_str = "|".join([p[1] for p in parses])
                out_file.write(word + ": " +parse_str + "\n")


def download_corpus_xml(out_filename):
    from opencorpora.cli import _download, FULL_CORPORA_URL_BZ2
    return _download(
        out_file=out_filename,
        decompress=True,
        disambig=False,
        url=FULL_CORPORA_URL_BZ2,
        verbose=True
    )


def estimate_tag_cpd(corpus_filename, out_path, min_word_freq, update_meta=True):
    from pymorphy2.opencorpora_dict.probability import (
        estimate_conditional_tag_probability, build_cpd_dawg)

    m = pymorphy2.MorphAnalyzer(out_path, probability_estimator_cls=None)

    logger.info("Estimating P(t|w) from %s" % corpus_filename)
    cpd, cfd = estimate_conditional_tag_probability(m, corpus_filename)

    logger.info("Encoding P(t|w) as DAWG")
    d = build_cpd_dawg(m, cpd, int(min_word_freq))
    dawg_filename = os.path.join(out_path, 'p_t_given_w.intdawg')
    d.save(dawg_filename)

    if update_meta:
        logger.info("Updating meta information")
        meta_filename = os.path.join(out_path, 'meta.json')
        meta = json_read(meta_filename)
        meta.extend([
            ('P(t|w)', True),
            ('P(t|w)_unique_words', len(cpd.conditions())),
            ('P(t|w)_outcomes', cfd.N()),
            ('P(t|w)_min_word_freq', int(min_word_freq)),
        ])
        json_write(meta_filename, meta)

    logger.info('\nDone.')


# =============================================================================

# Hacks are here to make docstring compatible with both
# docopt and sphinx.ext.autodoc.

head = """

Pymorphy2 is a morphological analyzer / inflection engine for Russian language.
"""
__doc__ ="""
Usage::

    pymorphy dict compile <DICT_XML> [--out <PATH>] [--force] [--verbose] [--min_ending_freq <NUM>] [--min_paradigm_popularity <NUM>] [--max_suffix_length <NUM>]
    pymorphy dict download_xml <OUT_FILE> [--verbose]
    pymorphy dict mem_usage [--dict <PATH>] [--verbose]
    pymorphy dict make_test_suite <XML_FILE> <OUT_FILE> [--limit <NUM>] [--verbose]
    pymorphy dict meta [--dict <PATH>]
    pymorphy prob download_xml <OUT_FILE> [--verbose]
    pymorphy prob estimate_cpd <CORPUS_XML> [--out <PATH>] [--min_word_freq <NUM>]
    pymorphy _parse <IN_FILE> <OUT_FILE> [--dict <PATH>] [--verbose]
    pymorphy -h | --help
    pymorphy --version

Options::

    -v --verbose                        Be more verbose
    -f --force                          Overwrite target folder
    -o --out <PATH>                     Output folder name [default: dict]
    --limit <NUM>                       Min. number of words per gram. tag [default: 100]
    --min_ending_freq <NUM>             Prediction: min. number of suffix occurances [default: 2]
    --min_paradigm_popularity <NUM>     Prediction: min. number of lexemes for the paradigm [default: 3]
    --max_suffix_length <NUM>           Prediction: max. length of prediction suffixes [default: 5]
    --min_word_freq <NUM>               P(t|w) estimation: min. word count in source corpus [default: 1]
    --dict <PATH>                       Dictionary folder path

"""
DOC = head + __doc__.replace('::\n', ':')


def main():
    """
    Pymorphy CLI interface dispatcher
    """
    from docopt import docopt
    args = docopt(DOC, version=pymorphy2.__version__)

    if args['--verbose']:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.debug(args)

    if args['_parse']:
        return _parse(args['--dict'], args['<IN_FILE>'], args['<OUT_FILE>'])

    elif args['dict']:
        if args['compile']:
            prediction_options = dict(
                (key, int(args['--'+key]))
                for key in ('min_ending_freq', 'min_paradigm_popularity', 'max_suffix_length')
            )
            return compile_dict(args['<DICT_XML>'], args['--out'], args['--force'], prediction_options)
        elif args['mem_usage']:
            return show_dict_mem_usage(args['--dict'], args['--verbose'])
        elif args['meta']:
            return show_dict_meta(args['--dict'])
        elif args['make_test_suite']:
            return make_test_suite(args['<XML_FILE>'], args['<OUT_FILE>'], int(args['--limit']))
        elif args['download_xml']:
            return download_dict_xml(args['<OUT_FILE>'], args['--verbose'])

    elif args['prob']:
        if args['download_xml']:
            return download_corpus_xml(args['<OUT_FILE>'])
        elif args['estimate_cpd']:
            return estimate_tag_cpd(args['<CORPUS_XML>'], args['--out'], args['--min_word_freq'])

