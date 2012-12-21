# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import collections
import itertools
import copy
import re
import codecs

from pymorphy2.opencorpora_dict import _load_json_or_xml_dict

logger = logging.getLogger(__name__)


def _get_word_parses(lemmas):
    word_parses = collections.defaultdict(list) # word -> possible tags

    for index, lemma_id in enumerate(lemmas):
        lemma = lemmas[lemma_id]
        for word, tag in lemma:
            word_parses[word].append(tag)

    return word_parses


def _add_ee_parses(word_parses):

    def combinations_of_all_lengths(it):
        return itertools.chain(
            *(itertools.combinations(it, num+1) for num in range(len(it)))
        )

    def replace_chars(word, positions, replacement):
        word_list = list(word)
        for pos in positions:
            word_list[pos] = replacement
        return "".join(word_list)

    def missing_umlaut_variants(word):
        umlaut_positions = [m.start() for m in re.finditer('Ё', word, re.U)]
        for positions in combinations_of_all_lengths(umlaut_positions):
            yield replace_chars(word, positions, 'Е')


    _word_parses = copy.deepcopy(word_parses)

    for word in word_parses:
        parses = word_parses[word]

        for word_variant in missing_umlaut_variants(word):
            _word_parses[word_variant].extend(parses)

    return _word_parses


def _get_test_suite(word_parses, word_limit=100):
    """
    Limit word_parses to ``word_limit`` words per tag.
    """
    gramtab = collections.Counter() # tagset -> number of stored items
    result = list()
    for word in word_parses:
        parses = word_parses[word]
        gramtab.update(parses)
        if any(gramtab[tag] < word_limit for tag in parses):
            result.append((word, parses))

    return result


def _save_test_suite(path, suite, revision):
    with codecs.open(path, 'w', 'utf8') as f:
        f.write("%s\n" % revision)
        for word, parses in suite:
            txt = "|".join([word]+parses) +'\n'
            f.write(txt)


def make_test_suite(opencorpora_dict_path, out_path, word_limit=100):
    """
    Extract test data from OpenCorpora .xml dictionary (at least
    ``word_limit`` words for each distinct gram. tag) and save it to a file.
    """
    logger.debug('loading dictionary to memory...')
    lemmas, links, grammemes, version, revision = _load_json_or_xml_dict(opencorpora_dict_path)

    logger.debug('preparing...')
    parses = _get_word_parses(lemmas)

    logger.debug('dictionary size: %d', len(parses))

    logger.debug('handling umlauts...')
    parses = _add_ee_parses(parses)
    logger.debug('dictionary size: %d', len(parses))

    logger.debug('building test suite...')
    suite = _get_test_suite(parses, word_limit)

    logger.debug('test suite size: %d', len(suite))

    logger.debug('saving...')
    _save_test_suite(out_path, suite, revision)
