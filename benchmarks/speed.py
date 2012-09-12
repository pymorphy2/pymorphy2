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

    total_usages = sum(w[1] for w in words)

    logger.debug("benchmarking...")
    logger.debug("Words: %d, usages: %d", len(words), total_usages)

    def _run():
        for word, cnt in words:
            for x in range(cnt):
                morph.tag(word)

    logger.info("    tagger.tag: %0.0f words/sec", utils.measure(_run, total_usages, 1))



def bench_all(dict_path=None):
    """ Run all benchmarks """
    morph = tagger.Morph.load(dict_path)
    bench_tag(morph)