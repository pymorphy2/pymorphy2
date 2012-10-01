# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest
from pymorphy2 import tagger

TEST_DATA = [
    ('КОШКА', ['КОШКА']),
    ('КОШКЕ', ['КОШКА']),

    # в pymorphy 0.5.6 результат парсинга - наоборот, сначала СТАЛЬ, потом СТАТЬ
    ('СТАЛИ', ['СТАТЬ', 'СТАЛЬ']),

    ('НАИСТАРЕЙШИЙ', ['СТАРЫЙ']),

    ('КОТЁНОК', ['КОТЁНОК']),
    ('КОТЕНОК', ['КОТЁНОК']),
    ('ТЯЖЕЛЫЙ', ['ТЯЖЁЛЫЙ']),
    ('ЛЕГОК', ['ЛЁГКИЙ']),

    ('ОНА', ['ОНА']),
    ('ЕЙ', ['ОНА']),
    ('Я', ['Я']),
    ('МНЕ', ['Я']),

    ('НАИНЕВЕРОЯТНЕЙШИЙ', ['ВЕРОЯТНЫЙ']),
    ('ЛУЧШИЙ', ['ХОРОШИЙ']),
    ('НАИЛУЧШИЙ', ['ХОРОШИЙ']),
    ('ЧЕЛОВЕК', ['ЧЕЛОВЕК']),
    ('ЛЮДИ', ['ЧЕЛОВЕК']),

    ('КЛЮЕВУ', ['КЛЮЕВ']),
    ('КЛЮЕВА', ['КЛЮЕВ']),

    ('ГУЛЯЛ', ['ГУЛЯТЬ']),
    ('ГУЛЯЛА', ['ГУЛЯТЬ']),
    ('ГУЛЯЕТ', ['ГУЛЯТЬ']),
    ('ГУЛЯЮТ', ['ГУЛЯТЬ']),
    ('ГУЛЯЛИ', ['ГУЛЯТЬ']),
    ('ГУЛЯТЬ', ['ГУЛЯТЬ']),

    ('ГУЛЯЮЩИЙ', ['ГУЛЯТЬ']),
    ('ГУЛЯВШИ', ['ГУЛЯТЬ']),
    ('ГУЛЯЯ', ['ГУЛЯТЬ']),
    ('ГУЛЯЮЩАЯ', ['ГУЛЯТЬ']),
    ('ЗАГУЛЯВШИЙ', ['ЗАГУЛЯТЬ']),

    ('КРАСИВЫЙ', ['КРАСИВЫЙ']),
    ('КРАСИВАЯ', ['КРАСИВЫЙ']),
    ('КРАСИВОМУ', ['КРАСИВЫЙ']),
    ('КРАСИВЫЕ', ['КРАСИВЫЙ']),

    ('ДЕЙСТВИЕ', ['ДЕЙСТВИЕ']),
]

PREFIX_PREDICTION_DATA = [
    ('ПСЕВДОКОШКА', ['ПСЕВДОКОШКА']),
    ('ПСЕВДОКОШКОЙ', ['ПСЕВДОКОШКА']),

    ('СВЕРХНАИСТАРЕЙШИЙ', ['СВЕРХСТАРЫЙ']),
    ('СВЕРХНАИСТАРЕЙШИЙ', ['СВЕРХСТАРЫЙ']),
    ('КВАЗИПСЕВДОНАИСТАРЕЙШЕГО', ['КВАЗИПСЕВДОСТАРЫЙ']),
    ('НЕБЕСКОНЕЧЕН', ['НЕБЕСКОНЕЧНЫЙ']),

    ('МЕГАКОТУ', ['МЕГАКОТ']),
    ('МЕГАСВЕРХНАИСТАРЕЙШЕМУ', ['МЕГАСВЕРХСТАРЫЙ']),
]

PREDICTION_TEST_DATA = [
    ('ТРИЖДЫЧЕРЕЗПИЛЮЛЮОКНАМИ', ['ТРИЖДЫЧЕРЕЗПИЛЮЛЮОКНО']),
    ('РАЗКВАКАЛИСЬ', ['РАЗКВАКАТЬСЯ']),
    ('КАШИВАРНЕЕ', ['КАШИВАРНЫЙ']),
    ('ДЕПЫРТАМЕНТОВ', ['ДЕПЫРТАМЕНТ']),
    ('ИЗМОХРАТИЛСЯ', ['ИЗМОХРАТИТЬСЯ']),

    ('БУТЯВКОЙ', ['БУТЯВКА', 'БУТЯВКОЙ']), # и никаких местоимений!
    ('САПАЮТ', ['САПАТЬ']), # и никаких местоимений!
]

morph = tagger.Morph.load()

def with_test_data(data):
    return pytest.mark.parametrize(
        ("word", "parse_result"),
        data
    )

class TestNormalForms(object):

    @with_test_data(TEST_DATA)
    def test_normal_forms(self, word, parse_result):
        assert morph.normal_forms(word) == parse_result

    @with_test_data(PREDICTION_TEST_DATA)
    def test_normal_forms_prediction(self, word, parse_result):
        assert morph.normal_forms(word) == parse_result

    @with_test_data(PREFIX_PREDICTION_DATA)
    def test_normal_forms_prefix_prediction(self, word, parse_result):
        assert morph.normal_forms(word) == parse_result


class TestTagWithPrefix(object):

    def test_tag_with_unknown_prefix(self):
        word = 'МЕГАКОТ'
        parse1 = morph._tag_as_word_with_unknown_prefix(word)
        parse2 = morph._tag_as_word_with_known_prefix(word)
        assert parse1 == parse2
