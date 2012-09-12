# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import codecs
import os
import pytest

from pymorphy2 import tagger, data, cli

SUITE_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'dev_data',
    'suite.txt'
)

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

suite70k = load_suite(SUITE_PATH)
morph = tagger.Morph.load()

def test_tagger():
    for word, tags in suite70k:
        parse_result = set(morph.tag(word))
        assert parse_result == tags
