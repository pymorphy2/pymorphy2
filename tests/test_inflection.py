# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest

from pymorphy2.shapes import restore_capitalization


def with_test_data(data):
    return pytest.mark.parametrize(
        ("word", "grammemes", "result"),
        data
    )


def assert_first_inflected_variant(word, grammemes, result, morph):
    inflected_variants = [p.inflect(set(grammemes)) for p in morph.parse(word)]
    inflected_variants = [v for v in inflected_variants if v]
    # inflected_variants = morph.inflect(word, grammemes)
    assert len(inflected_variants)

    inflected = inflected_variants[0]
    assert restore_capitalization(inflected.word, word) == result


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

    # частицы - не отрезаются
    ('скажи-ка', ['futr'], 'скажу-ка'),
])
def test_first_inflected_value(word, grammemes, result, morph):
    assert_first_inflected_variant(word, grammemes, result, morph)


def test_orel(morph):
    assert_first_inflected_variant('орел', ['gent'], 'орла', morph)


@with_test_data([
    ('снег', ['gent'], 'снега'),
    ('снег', ['gen2'], 'снегу'),
    ('Боря', ['voct'], 'Борь'),
])
def test_second_cases(word, grammemes, result, morph):
    assert_first_inflected_variant(word, grammemes, result, morph)


@with_test_data([
    ('валенок', ['gent', 'sing'], 'валенка'),
    ('валенок', ['gen2', 'sing'], 'валенка'),  # there is no gen2
    ('велосипед', ['loct'], 'велосипеде'), # о велосипеде
    ('велосипед', ['loc2'], 'велосипеде'), # а тут второго предложного нет, в велосипеде
    ('хомяк', ['voct'], 'хомяк'),        # there is not voct, nomn should be used
    ('Геннадий', ['voct'], 'Геннадий'),  # there is not voct, nomn should be used
])
def test_case_substitution(word, grammemes, result, morph):
    assert_first_inflected_variant(word, grammemes, result, morph)


@pytest.mark.xfail
@with_test_data([
    # доп. падежи, fixme
    ('лес', ['loct'], 'лесе'),   # о лесе
    ('лес', ['loc2'], 'лесу'),   # в лесу
    ('острова', ['datv'], 'островам'),
])
def test_best_guess(word, grammemes, result, morph):
    assert_first_inflected_variant(word, grammemes, result, morph)


@with_test_data([
    ('заснеженный', ['gent'], 'заснеженного'),  # не "заснежённого"
    ('ведро', ['gent'], 'ведра'),  # не "вёдра"
])
def test_not_informal(word, grammemes, result, morph):
    assert_first_inflected_variant(word, grammemes, result, morph)
