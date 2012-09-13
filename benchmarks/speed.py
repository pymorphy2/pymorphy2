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

def bench_tag(morph):
    logger.debug("loading benchmark data...")
    words = load_words()
    word_no_umlauts = [(w[0].replace('Ё', 'Е'), w[1]) for w in words]

    total_usages = sum(w[1] for w in words)

    logger.debug("benchmarking...")
    logger.debug("Words: %d, usages: %d", len(words), total_usages)

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

    logger.info("    tagger.tag: %0.0f words/sec (with freq. info)", utils.measure(_run, total_usages, 1))
    logger.info("    tagger.tag: %0.0f words/sec (without freq. info)", utils.measure(_run_nofreq, len(words), 3))
    logger.info("    tagger.tag: %0.0f words/sec (without freq. info, no umlauts)", utils.measure(_run_no_umlauts, len(words), 3))



def bench_all(dict_path=None):
    """ Run all benchmarks """
    morph = tagger.Morph.load(dict_path)
    bench_tag(morph)