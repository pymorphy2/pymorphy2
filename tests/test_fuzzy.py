# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import codecs
import os
import pytest

from .utils import morph

SUITE_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'dev_data',
    'suite.txt'
)

Tag = morph.TagClass

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


def test_tagger_fuzzy():
    if not os.path.exists(SUITE_PATH):
        msg = """
        Fuzzy test suite was not created. In order to run
        "fuzzy" tests create a test suite with the following command:

            pymorphy dict make_test_suite dict.xml dev_data/suite.txt -v

        """
        pytest.skip(msg)

    suite_revision, suite70k = load_suite(SUITE_PATH)
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
