# -*- coding: utf-8 -*-
import pytest


@pytest.fixture(scope='session')
def morph():
    import pymorphy2
    return pymorphy2.MorphAnalyzer()


@pytest.fixture(scope='session')
def Tag(morph):
    return morph.TagClass
