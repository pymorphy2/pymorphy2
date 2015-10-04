# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest

import pymorphy2
from pymorphy2.analyzer import lang_dict_path


def test_old_dictionaries_supported():
    pytest.importorskip("pymorphy2_dicts")
    m = pymorphy2.MorphAnalyzer(lang='ru-old')
    assert m.lang == 'ru-old'
    assert m.tag('стиль')[0].POS == 'NOUN'


def test_old_dictionaries_not_installed():
    try:
        import pymorphy2_dicts
        pytest.skip("pymorphy2_dicts package is installed")
    except ImportError:
        pass

    with pytest.raises(ValueError):
        pymorphy2.MorphAnalyzer(lang='ru-old')


def test_old_dictionaries_supported_by_path():
    pymorphy2_dicts = pytest.importorskip("pymorphy2_dicts")
    m = pymorphy2.MorphAnalyzer(pymorphy2_dicts.get_path())
    assert m.lang == 'ru'
    assert m.tag('стиль')[0].POS == 'NOUN'


def test_morph_analyzer_bad_path():
    with pytest.raises(IOError):
        pymorphy2.MorphAnalyzer("/sdfgsd/gdsfgsdfg/dfgdsfg/dsfgsdfg/as")


def test_language_from_dict():
    ru_path = lang_dict_path('ru')
    m = pymorphy2.MorphAnalyzer(path=ru_path)
    assert m.lang == 'ru'


def test_bad_language():
    with pytest.raises(ValueError):
        pymorphy2.MorphAnalyzer(lang='something-unsupported')


def test_nonmatching_language():
    ru_path = lang_dict_path('ru')
    m = pymorphy2.MorphAnalyzer(path=ru_path, lang='uk')
    assert 'Init' in m.parse('Ї')[0].tag
    assert m.lang == 'uk'
