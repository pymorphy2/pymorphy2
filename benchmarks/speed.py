# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import logging
import codecs
import os
import functools
import datetime

from pymorphy2 import MorphAnalyzer
from benchmarks import utils

logger = logging.getLogger('pymorphy2.bench')

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'dev_data',
    'unigrams.txt'
)

def load_words(path=DATA_PATH):
    words = []
    with codecs.open(path, 'r', 'utf8') as f:
        for line in f:
            word, count, ipm = line.split()
            count = int(count)
            words.append((word.lower(), count))
    return words

def get_total_usages(words):
    return sum(w[1] for w in words)

def bench_tag(morph, words, total_usages, repeats):
    word_no_umlauts = [(w[0].replace('ё', 'е'), w[1]) for w in words]

    def _run():
        for word, cnt in words:
            for x in range(cnt):
                morph.tag(word)

    def _run_nofreq():
        for word, cnt in words:
            morph.tag(word)

    def _run_no_umlauts():
        for word, cnt in word_no_umlauts:
            morph.tag(word)

    def _run_str():
        for word, cnt in words:
            str(morph.tag(word))

    measure = functools.partial(utils.measure, repeats=repeats)

    logger.info("    morph.tag: %0.0f words/sec (with freq. info)", measure(_run, total_usages))
    logger.info("    morph.tag: %0.0f words/sec (without freq. info)", measure(_run_nofreq, len(words)))
    logger.info("    morph.tag: %0.0f words/sec (without freq. info, umlauts removed from input)", measure(_run_no_umlauts, len(words)))
    logger.info("    morph.tag: %0.0f words/sec (without freq. info, str(tag) called)", measure(_run_str, len(words)))


def bench_parse(morph, words, total_usages, repeats):
    def _run():
        for word, cnt in words:
            for x in range(cnt):
                morph.parse(word)

    def _run_nofreq():
        for word, cnt in words:
            morph.parse(word)

    measure = functools.partial(utils.measure, repeats=repeats)

    logger.info("    morph.parse: %0.0f words/sec (with freq. info)", measure(_run, total_usages))
    logger.info("    morph.parse: %0.0f words/sec (without freq. info)", measure(_run_nofreq, len(words)))

def bench_all(dict_path=None, repeats=5):
    """ Run all benchmarks """
    logger.debug("loading MorphAnalyzer...")
    morph = MorphAnalyzer(dict_path)
    morph_plain = MorphAnalyzer(dict_path, result_type=None)

    logger.debug("loading benchmark data...")
    words = load_words()
    total_usages = get_total_usages(words)

    logger.debug("Words: %d, usages: %d", len(words), total_usages)

    start_time = datetime.datetime.now()

    logger.info("\nbenchmarking MorphAnalyzer():")
    bench_parse(morph, words, total_usages, repeats)
    bench_tag(morph, words, total_usages, repeats)

    logger.info("\nbenchmarking MorphAnalyzer(result_type=None):")
    bench_parse(morph_plain, words, total_usages, repeats)

    end_time = datetime.datetime.now()
    logger.info("\n----\nDone in %s.\n" % (end_time-start_time))
