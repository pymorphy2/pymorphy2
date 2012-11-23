# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest
import copy

from .utils import morph

def with_test_data(data):
    return pytest.mark.parametrize(
        ("word", "grammemes", "result"),
        data
    )

def assert_first_inflected_variant(word, grammemes, result):
    inflected_variants = morph.inflect(word, grammemes)
    assert len(inflected_variants)

    inflected = inflected_variants[0]
    assert inflected[0] == result


@with_test_data([
    # суслики и бутявки
    ("СУСЛИК", ["datv"], "СУСЛИКУ"),
    ("СУСЛИКИ", ["datv"], "СУСЛИКАМ"),
    ("СУСЛИКОВ", ["datv"], "СУСЛИКАМ"),
    ("СУСЛИКА", ["datv"], "СУСЛИКУ"),
    ("СУСЛИК", ["datv", "plur"], "СУСЛИКАМ"),

    ("БУТЯВКА", ["datv"], "БУТЯВКЕ"),
    ("БУТЯВОК", ["datv"], "БУТЯВКАМ"),

    # глаголы, причастия, деепричастия
    ("ГУЛЯЮ", ["past"], "ГУЛЯЛ"),
    ("ГУЛЯЛ", ["pres"], "ГУЛЯЮ"),
    ("ГУЛЯЛ", ["INFN"], "ГУЛЯТЬ"),
    ("ГУЛЯЛ", ["GRND"], "ГУЛЯВ"),
    ("ГУЛЯЛ", ["PRTF"], "ГУЛЯВШИЙ"),
    ("ГУЛЯЛА", ["PRTF"], "ГУЛЯВШАЯ"),
    ("ГУЛЯЮ", ["PRTF", "datv"], "ГУЛЯЮЩЕМУ"),
    ("ГУЛЯВШИЙ", ["VERB"], "ГУЛЯЛ"),
    ("ГУЛЯВШИЙ", ["VERB", "femn"], "ГУЛЯЛА"),
    ("ИДУ", ["2per"], "ИДЁШЬ"),
    ("ИДУ", ["2per", "plur"], "ИДЁТЕ"),
    ("ИДУ", ["3per"], "ИДЁТ"),
    ("ИДУ", ["3per", "plur"], "ИДУТ"),
    ("ИДУ", ["impr", "excl"], "ИДИ"),

    # баг из pymorphy
    ('КИЕВ', ['loct'], 'КИЕВЕ'),

    # одушевленность
    ('СЛАБЫЙ', ['accs', 'inan'], 'СЛАБЫЙ'),
    ('СЛАБЫЙ', ['accs', 'anim'], 'СЛАБОГО'),

    # сравнительные степени прилагательных
    ('БЫСТРЫЙ', ['COMP'], 'БЫСТРЕЕ'),
    ('ХОРОШАЯ', ['COMP'], 'ЛУЧШЕ'),
])
def test_first_inflected_value(word, grammemes, result):
    assert_first_inflected_variant(word, grammemes, result)


@pytest.mark.xfail
@with_test_data([
    # доп. падежи, fixme
    ('ЛЕС', ['loct'], 'ЛЕСЕ'),   # о лесе
    ('ЛЕС', ['loc2'], 'ЛЕСУ'),   # в лесу
    ('ВЕЛОСИПЕД', ['loct'], 'ВЕЛОСИПЕДЕ'), # о велосипеде
    ('ВЕЛОСИПЕД', ['loc2'], 'ВЕЛОСИПЕДЕ'), # а тут второго предложного нет, в велосипеде
])
def test_loc2(word, grammemes, result):
    assert_first_inflected_variant(word, grammemes, result)

def test_orel():
    assert_first_inflected_variant('ОРЕЛ', ['gent'], 'ОРЛА')

@pytest.mark.xfail
def test_best_guess():
    assert_first_inflected_variant('ОСТРОВА', ['datv'], 'ОСТРОВАМ')