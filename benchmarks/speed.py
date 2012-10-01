# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import logging
import codecs
import os

from pymorphy2 import tagger
from benchmarks import utils

logger = logging.getLogger('pymorphy2.bench')

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'dev_data',
    'unigrams.cyr.lc'
)

def load_words(path=DATA_PATH):
    words = []
    with codecs.open(path, 'r', 'utf8') as f:
        for line in f:
            word, count, ipm = line.split()
            count = int(count)
            words.append((word.upper(), count))
    return words

def get_total_usages(words):
    return sum(w[1] for w in words)

def bench_tag(morph, words, total_usages):
    word_no_umlauts = [(w[0].replace('Ё', 'Е'), w[1]) for w in words]

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

    logger.info("    tagger.tag: %0.0f words/sec (with freq. info)", utils.measure(_run, total_usages, 3))
    logger.info("    tagger.tag: %0.0f words/sec (without freq. info)", utils.measure(_run_nofreq, len(words), 3))
    logger.info("    tagger.tag: %0.0f words/sec (without freq. info, input umlauts removed)", utils.measure(_run_no_umlauts, len(words), 3))


def bench_parse(morph, words, total_usages):
    def _run():
        for word, cnt in words:
            for x in range(cnt):
                morph.parse(word)

    def _run_nofreq():
        for word, cnt in words:
            morph.parse(word)

    logger.info("    tagger.parse: %0.0f words/sec (with freq. info)", utils.measure(_run, total_usages, 3))
    logger.info("    tagger.parse: %0.0f words/sec (without freq. info)", utils.measure(_run_nofreq, len(words), 3))

def bench_all(dict_path=None):
    """ Run all benchmarks """
    logger.debug("loading tagger...")
    morph = tagger.Morph.load(dict_path)

    logger.debug("loading benchmark data...")
    words = load_words()
    total_usages = get_total_usages(words)

    logger.debug("Words: %d, usages: %d", len(words), total_usages)

    logger.debug("benchmarking...")
    bench_parse(morph, words, total_usages)
    bench_tag(morph, words, total_usages)
