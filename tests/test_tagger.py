# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest
from pymorphy2 import tagger, tagset

morph = tagger.Morph.load()

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
    ('ДЕПЫРТАМЕНТОВ', ['ДЕПЫРТАМЕНТ', 'ДЕПЫРТАМЕНТОВЫЙ']),
    ('ИЗМОХРАТИЛСЯ', ['ИЗМОХРАТИТЬСЯ']),

    ('БУТЯВКОЙ', ['БУТЯВКА', 'БУТЯВКОЙ']), # и никаких местоимений!
    ('САПАЮТ', ['САПАТЬ']), # и никаких местоимений!
]

NON_PRODUCTIVE_BUGS_DATA = [
    ('БЯКОБЫ', 'PRCL'),
    ('БЯКОБЫ', 'CONJ'),
    ('ПСЕВДОЯКОБЫ', 'PRCL'),
    ('ПСЕВДОЯКОБЫ', 'CONJ'),
]

def with_test_data(data, second_param_name='parse_result'):
    return pytest.mark.parametrize(
        ("word", second_param_name),
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


class TestTagMethod(object):

    def _tagged_as(self, parse, cls):
        return any(tagset.get_POS(p)==cls for p in parse)

    def assertNotTaggedAs(self, word, cls):
        parse = morph.tag(word)
        assert not self._tagged_as(parse, cls), (parse, cls)

    def _tags_from_parses(self, parses):
        return [p[1] for p in parses]

    @with_test_data(TEST_DATA)
    def test_tag_is_on_par_with_parse(self, word, parse_result): #parse_result is unused here
        assert set(morph.tag(word)) == set(self._tags_from_parses(morph.parse(word)))

    @with_test_data(PREDICTION_TEST_DATA)
    def test_tag_is_on_par_with_parse__prediction(self, word, parse_result): #parse_result is unused here
        assert set(morph.tag(word)) == set(self._tags_from_parses(morph.parse(word)))

    @with_test_data(PREFIX_PREDICTION_DATA)
    def test_tag_is_on_par_with_parse__prefix_prediction(self, word, parse_result): #parse_result is unused here
        assert set(morph.tag(word)) == set(self._tags_from_parses(morph.parse(word)))

    @with_test_data(NON_PRODUCTIVE_BUGS_DATA, 'cls')
    def test_no_nonproductive_forms(self, word, cls):
        self.assertNotTaggedAs(word, cls)


class TestParse(object):

    def _parsed_as(self, parse, cls):
        return any(tagset.get_POS(p[1])==cls for p in parse)

    def _parse_cls_first_index(self, parse, cls):
        for idx, p in enumerate(parse):
            if tagset.get_POS(p[1]) == cls:
                return idx

    def assertNotParsedAs(self, word, cls):
        parse = morph.parse(word)
        assert not self._parsed_as(parse, cls), (parse, cls)

    @with_test_data(NON_PRODUCTIVE_BUGS_DATA, 'cls')
    def test_no_nonproductive_forms(self, word, cls):
        self.assertNotParsedAs(word, cls)

    def test_no_duplicate_parses(self):
        parse = morph.parse('БУТЯВКОЙ')
        data = [variant[:3] for variant in parse]
        assert len(set(data)) == len(data), parse

    def test_parse_order(self):
        parse = morph.parse('ПРОДЮСЕРСТВО')
        assert self._parsed_as(parse, 'NOUN')
        assert self._parsed_as(parse, 'ADVB')
        assert self._parse_cls_first_index(parse, 'NOUN') < self._parse_cls_first_index(parse, 'ADVB')


class TestTagWithPrefix(object):

    def test_tag_with_unknown_prefix(self):
        word = 'МЕГАКОТ'
        parse1 = morph._tag_as_word_with_unknown_prefix(word)
        parse2 = morph._tag_as_word_with_known_prefix(word)
        assert parse1 == parse2
