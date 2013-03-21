# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import collections
import copy
import re
import codecs

from pymorphy2.opencorpora_dict.parse import parse_opencorpora_xml
from pymorphy2.utils import combinations_of_all_lengths

logger = logging.getLogger(__name__)


def _get_word_parses(lexemes):
    word_parses = collections.defaultdict(list) # word -> possible tags

    for index, lex_id in enumerate(lexemes):
        lexeme = lexemes[lex_id]
        for word, tag in lexeme:
            word_parses[word].append(tag)

    return word_parses


def _add_ee_parses(word_parses):

    def replace_chars(word, positions, replacement):
        chars = list(word)
        for pos in positions:
            chars[pos] = replacement
        return "".join(chars)

    def variants_with_missing_umlauts(word):
        umlaut_positions = [m.start() for m in re.finditer('ё', word, re.U)]
        for positions in combinations_of_all_lengths(umlaut_positions):
            yield replace_chars(word, positions, 'е')


    _word_parses = copy.deepcopy(word_parses)

    for word in word_parses:
        parses = word_parses[word]

        for word_variant in variants_with_missing_umlauts(word):
            _word_parses[word_variant].extend(parses)

    return _word_parses


def _get_test_suite(word_parses, word_limit=100):
    """
    Limit word_parses to ``word_limit`` words per tag.
    """
    gramtab = collections.defaultdict(int)  # tagset -> number of stored items
    result = list()
    for word in word_parses:
        tags = word_parses[word]
        for tag in tags:
            gramtab[tag] += 1
        if any(gramtab[tag] < word_limit for tag in tags):
            result.append((word, tags))

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
    parsed_dict = parse_opencorpora_xml(opencorpora_dict_path)

    logger.debug('preparing...')
    parses = _get_word_parses(parsed_dict.lexemes)

    logger.debug('dictionary size: %d', len(parses))

    logger.debug('handling umlauts...')
    parses = _add_ee_parses(parses)
    logger.debug('dictionary size: %d', len(parses))

    logger.debug('building test suite...')
    suite = _get_test_suite(parses, word_limit)

    logger.debug('test suite size: %d', len(suite))

    logger.debug('saving...')
    _save_test_suite(out_path, suite, parsed_dict.revision)
