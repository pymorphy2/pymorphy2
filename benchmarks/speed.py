# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import logging
import codecs
import os

from pymorphy2 import data, tagger
from benchmarks import utils

logger = logging.getLogger('pymorphy2.bench')

DATA_PATH = os.path.join(os.path.dirname(__file__), 'unigrams.cyr.lc')
DICT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'ru.dct')
)

def get_dict():
    return data.load_dict(DICT_PATH)

dct = get_dict()

def load_words(path=DATA_PATH):
    words = []
    with codecs.open(path, 'r', 'utf8') as f:
        for line in f:
            word, count, ipm = line.split()
            count = int(count)
            words.append((word.upper(), count))
    return words

def bench_tag():
    logger.debug("loading benchmark data...")
    all_words = load_words()

    words = all_words

    total_usages = sum(w[1] for w in words)

    logger.debug("benchmarking...")
    logger.debug("Words: %d, usages: %d", len(words), total_usages)

    morph = tagger.Morph(dct)

    def _run():
        for word, cnt in words:
            for x in range(cnt):
                morph.tag(word)

    logger.info("    tagger.tag: %0.0f words/sec", utils.measure(_run, total_usages, 1))



def bench_all():
    """ Run all benchmarks """
    bench_tag()