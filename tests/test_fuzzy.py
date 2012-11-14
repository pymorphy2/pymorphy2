# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import codecs
import os
import pytest

from pymorphy2 import tagger

SUITE_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'dev_data',
    'suite.txt'
)

morph = tagger.Morph.load()
Tag = morph.tag_class()

def iter_suite(path):
    """
    loads test suite
    """
    with codecs.open(path, 'r', 'utf8') as f:
        for index, line in enumerate(f):
            line = line.strip("\n")

            if index == 0: # revision
                yield line
                continue

            # test data
            parts = line.split('|')
            word, tags = parts[0], [Tag(tag) for tag in parts[1:]]
            yield word, tags

def load_suite(path):
    suite = list(iter_suite(path))
    return suite[0], suite[1:]

suite_revision, suite70k = load_suite(SUITE_PATH)

def test_tagger_fuzzy():
    dict_revision = morph.meta()['source_revision']
    if suite_revision != dict_revision:
        msg = """
        Test suite revision (%s) doesn't match dictionary revision (%s).
        Regenerate test suite with the following command:

            pymorphy dict make_test_suite dict.xml dev_data/suite.txt -v

        """  % (suite_revision, dict_revision)
        pytest.skip(msg)

    for word, tags in suite70k:
        parse_result = set(morph.tag(word))
        assert parse_result == set(tags)
