# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import codecs
import pytest

from pymorphy2 import tagger, data, cli

def iter_suite(path):
    """
    loads test suite
    """
    with codecs.open(path, 'r', 'utf8') as f:
        for line in f:
            parts = line.strip('\n').split('|')
            word, tags = parts[0], set(parts[1:])
            yield word, tags

def load_suite(path):
    return list(iter_suite(path))


suite70k = load_suite('tests/data/suite.txt')
dct = data.load_dict('ru.dict')


def test_tagger():
    for word, tags in suite70k:
        parse_result = set(tagger.tag(dct, word))
        assert parse_result == tags

