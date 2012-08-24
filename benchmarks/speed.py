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
    os.path.join(os.path.dirname(__file__), '..', 'ru.dict')
)

def get_dict():
    return data.load_dict(DICT_PATH)

def load_words(path=DATA_PATH):
    words = []
    with codecs.open(path, 'r', 'utf8') as f:
        for line in f:
            word, count, ipm = line.split()
            count = int(count)
            words.append((word.upper(), count))
    return words

def scale_usages(words, result_size):
    total = sum(w[1] for w in words) + len(words)  # add-one smoothing
    return [(w[0], int(round((w[1]+1)*result_size/total))) for w in words]

def bench_tag():
    logger.debug("loading benchmark data...")
    all_words = load_words()

    words = all_words#[0:2000]
    #words = scale_usages(words, corpus_size)

    total_usages = sum(w[1] for w in words)

    logger.debug("benchmarking...")
    logger.debug("Words: %d, usages: %d", len(words), total_usages)

    def _run():
        for word, cnt in words:
            for x in range(cnt):
                tagger.tag(dct, word)

    logger.info("    tagger.tag: %0.0f words/sec", utils.measure(_run, total_usages, 1))



def bench_all():
    """ Run all benchmarks """
    bench_tag()