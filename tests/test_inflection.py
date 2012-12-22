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
    ("суслик", ["datv"], "суслику"),
    ("суслики", ["datv"], "сусликам"),
    ("сусликов", ["datv"], "сусликам"),
    ("суслика", ["datv"], "суслику"),
    ("суслик", ["datv", "plur"], "сусликам"),

    ("бутявка", ["datv"], "бутявке"),
    ("бутявок", ["datv"], "бутявкам"),

    # глаголы, причастия, деепричастия
    ("гуляю", ["past"], "гулял"),
    ("гулял", ["pres"], "гуляю"),
    ("гулял", ["INFN"], "гулять"),
    ("гулял", ["GRND"], "гуляв"),
    ("гулял", ["PRTF"], "гулявший"),
    ("гуляла", ["PRTF"], "гулявшая"),
    ("гуляю", ["PRTF", "datv"], "гуляющему"),
    ("гулявший", ["VERB"], "гулял"),
    ("гулявший", ["VERB", "femn"], "гуляла"),
    ("иду", ["2per"], "идёшь"),
    ("иду", ["2per", "plur"], "идёте"),
    ("иду", ["3per"], "идёт"),
    ("иду", ["3per", "plur"], "идут"),
    ("иду", ["impr", "excl"], "иди"),

    # баг из pymorphy
    ('киев', ['loct'], 'киеве'),

    # одушевленность
    ('слабый', ['accs', 'inan'], 'слабый'),
    ('слабый', ['accs', 'anim'], 'слабого'),

    # сравнительные степени прилагательных
    ('быстрый', ['COMP'], 'быстрее'),
    ('хорошая', ['COMP'], 'лучше'),
])
def test_first_inflected_value(word, grammemes, result):
    assert_first_inflected_variant(word, grammemes, result)


@pytest.mark.xfail
@with_test_data([
    # доп. падежи, fixme
    ('лес', ['loct'], 'лесе'),   # о лесе
    ('лес', ['loc2'], 'лесу'),   # в лесу
    ('велосипед', ['loct'], 'велосипеде'), # о велосипеде
    ('велосипед', ['loc2'], 'велосипеде'), # а тут второго предложного нет, в велосипеде
])
def test_loc2(word, grammemes, result):
    assert_first_inflected_variant(word, grammemes, result)

def test_orel():
    assert_first_inflected_variant('орел', ['gent'], 'орла')

@pytest.mark.xfail
def test_best_guess():
    assert_first_inflected_variant('острова', ['datv'], 'островам')