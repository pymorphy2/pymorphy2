# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest

from .utils import morph

TEST_DATA = [
    ('кошка', ['кошка']),
    ('кошке', ['кошка']),

    # в pymorphy 0.5.6 результат парсинга - наоборот, сначала СТАЛЬ, потом СТАТЬ
    ('стали', ['стать', 'сталь']),

    ('наистарейший', ['старый']),

    ('котёнок', ['котёнок']),
    ('котенок', ['котёнок']),
    ('тяжелый', ['тяжёлый']),
    ('легок', ['лёгкий']),

    ('она', ['она']),
    ('ей', ['она']),
    ('я', ['я']),
    ('мне', ['я']),

    ('наиневероятнейший', ['вероятный']),
    ('лучший', ['хороший']),
    ('наилучший', ['хороший']),
    ('человек', ['человек']),
    ('люди', ['человек']),

    ('клюеву', ['клюев']),
    ('клюева', ['клюев']),

    ('гулял', ['гулять']),
    ('гуляла', ['гулять']),
    ('гуляет', ['гулять']),
    ('гуляют', ['гулять']),
    ('гуляли', ['гулять']),
    ('гулять', ['гулять']),

    ('гуляющий', ['гулять']),
    ('гулявши', ['гулять']),
    ('гуляя', ['гулять']),
    ('гуляющая', ['гулять']),
    ('загулявший', ['загулять']),

    ('красивый', ['красивый']),
    ('красивая', ['красивый']),
    ('красивому', ['красивый']),
    ('красивые', ['красивый']),

    ('действие', ['действие']),
]

PREFIX_PREDICTION_DATA = [
    ('псевдокошка', ['псевдокошка']),
    ('псевдокошкой', ['псевдокошка']),

    ('сверхнаистарейший', ['сверхстарый']),
    ('сверхнаистарейший', ['сверхстарый']),
    ('квазипсевдонаистарейшего', ['квазипсевдостарый']),
    ('небесконечен', ['небесконечный']),

    ('мегакоту', ['мегакот']),
    ('мегасверхнаистарейшему', ['мегасверхстарый']),
]

PREDICTION_TEST_DATA = [
    ('триждычерезпилюлюокнами', ['триждычерезпилюлюокно']),
    ('разквакались', ['разквакаться']),
    ('кашиварнее', ['кашиварный']),
    ('депыртаментов', ['депыртамент', 'депыртаментовый']),
    ('измохратился', ['измохратиться']),

    ('бутявкой', ['бутявка', 'бутявкой']), # и никаких местоимений!
    ('сапают', ['сапать']), # и никаких местоимений!
]

NON_PRODUCTIVE_BUGS_DATA = [
    ('бякобы', 'PRCL'),
    ('бякобы', 'CONJ'),
    ('псевдоякобы', 'PRCL'),
    ('псевдоякобы', 'CONJ'),
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
        return any(tag.POS==cls for tag in parse)

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
        return any(p[1].POS==cls for p in parse)

    def _parse_cls_first_index(self, parse, cls):
        for idx, p in enumerate(parse):
            if p[1].POS == cls:
                return idx

    def assertNotParsedAs(self, word, cls):
        parse = morph.parse(word)
        assert not self._parsed_as(parse, cls), (parse, cls)

    @with_test_data(NON_PRODUCTIVE_BUGS_DATA, 'cls')
    def test_no_nonproductive_forms(self, word, cls):
        self.assertNotParsedAs(word, cls)

    def test_no_duplicate_parses(self):
        parse = morph.parse('бутявкой')
        data = [variant[:3] for variant in parse]
        assert len(set(data)) == len(data), parse

    def test_parse_order(self):
        parse = morph.parse('продюсерство')
        assert self._parsed_as(parse, 'NOUN')
        assert self._parsed_as(parse, 'ADVB')
        assert self._parse_cls_first_index(parse, 'NOUN') < self._parse_cls_first_index(parse, 'ADVB')


class TestTagWithPrefix(object):

    def test_tag_with_unknown_prefix(self):
        word = 'мегакот'
        parse1 = morph._tag_as_word_with_unknown_prefix(word)
        parse2 = morph._tag_as_word_with_known_prefix(word)
        assert parse1 == parse2
