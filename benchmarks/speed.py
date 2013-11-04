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

    logger.info("    morph.tag(w): %0.0f words/sec (considering word frequencies)", measure(_run, total_usages))
    logger.info("    morph.tag(w): %0.0f words/sec", measure(_run_nofreq, len(words)))
    logger.info("    morph.tag(w): %0.0f words/sec (umlauts removed from input)", measure(_run_no_umlauts, len(words)))
    logger.info("    morph.tag(w): %0.0f words/sec (str(tag) called)", measure(_run_str, len(words)))


def bench_parse(morph, words, total_usages, repeats):
    def _run():
        for word, cnt in words:
            for x in range(cnt):
                morph.parse(word)

    def _run_nofreq():
        for word, cnt in words:
            morph.parse(word)

    def _run_normal_form():
        for word, cnt in words:
            [p.normal_form for p in morph.parse(word)]

    def _run_normalized():
        for word, cnt in words:
            [p.normalized for p in morph.parse(word)]

    def _run_is_noun():
        for word, cnt in words:
            [set(['NOUN']) in p.tag for p in morph.parse(word)]

    def _run_is_noun2():
        for word, cnt in words:
            [p.tag.POS == 'NOUN' for p in morph.parse(word)]

    def _run_word_is_known():
        for x in range(10):
            for word, cnt in words:
                morph.word_is_known(word)

    def _run_cyr_repr():
        for word, cnt in words:
            [p.tag.cyr_repr for p in morph.parse(word)]

    def _run_grammemes_cyr():
        for word, cnt in words:
            [p.tag.grammemes_cyr for p in morph.parse(word)]

    def _run_POS_cyr():
        for word, cnt in words:
            [morph.lat2cyr(p.tag) for p in morph.parse(word)]

    def _run_lexeme():
        for word, cnt in words[::5]:
            [p.lexeme for p in morph.parse(word)]

    measure = functools.partial(utils.measure, repeats=repeats)

    def show_info(bench_name, func, note='', count=len(words)):
        wps = measure(func, count)
        logger.info("    %-50s %0.0f words/sec %s", bench_name, wps, note)


    # === run benchmarks:

    show_info('morph.parse(w)', _run_nofreq)
    show_info('morph.parse(w)', _run, '(considering word frequencies)', total_usages)

    if morph._result_type is not None:
        show_info('morph.word_is_known(w)', _run_word_is_known, count=len(words)*10)
        show_info("[p.normal_form for p in morph.parse(w)]", _run_normal_form)
        show_info("[p.normalized for p in morph.parse(w)]", _run_normalized)
        show_info("[p.lexeme for p in morph.parse(w)]", _run_lexeme, count=len(words)/5)
        show_info("[{'NOUN'} in p.tag for p in morph.parse(w)]", _run_is_noun)
        show_info("[p.tag.POS == 'NOUN' for p in morph.parse(w)]", _run_is_noun2)
        show_info("[p.tag.cyr_repr for p in morph.parse(word)]", _run_cyr_repr)
        show_info("[p.tag.grammemes_cyr for p in morph.parse(word)]", _run_grammemes_cyr)
        show_info("[morph.lat2cyr(p.tag) for p in morph.parse(word)]", _run_POS_cyr)

    logger.info("")


def bench_all(repeats, dict_path=None):
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
    logger.info("----\nDone in %s.\n" % (end_time-start_time))
