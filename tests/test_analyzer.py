# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest
import pymorphy2
from pymorphy2.predictors import UnknownPrefixPredictor, KnownPrefixPredictor

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
    ('покашиварней', ['кашиварный', 'покашиварный', 'покашиварня']),
    ('подкашиварней', ['дкашиварный', 'подкашиварный', 'подкашиварня']),
    ('депыртаментов', ['депыртамент', 'депыртаментовый']),
    ('измохратился', ['измохратиться']),

    ('бутявкой', ['бутявка', 'бутявкой']), # и никаких местоимений!
    ('сапают', ['сапать']), # и никаких местоимений!

    ('кюди', ['кюдить', 'кюдь', 'кюди']) # и никаких "человек"
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

class TestNormalForms:

    @with_test_data(TEST_DATA)
    def test_normal_forms(self, word, parse_result):
        assert morph.normal_forms(word) == parse_result

    @with_test_data(PREDICTION_TEST_DATA)
    def test_normal_forms_prediction(self, word, parse_result):
        assert morph.normal_forms(word) == parse_result

    @with_test_data(PREFIX_PREDICTION_DATA)
    def test_normal_forms_prefix_prediction(self, word, parse_result):
        assert morph.normal_forms(word) == parse_result


class TestTagMethod:

    def _tagged_as(self, tags, cls):
        return any(tag.POS == cls for tag in tags)

    def assertNotTaggedAs(self, word, cls):
        tags = morph.tag(word)
        assert not self._tagged_as(tags, cls), (tags, cls)

    @with_test_data(TEST_DATA)
    def test_tag_is_on_par_with_parse(self, word, parse_result): #parse_result is unused here
        assert set(morph.tag(word)) == set(p.tag for p in morph.parse(word))


    @with_test_data(PREDICTION_TEST_DATA)
    def test_tag_is_on_par_with_parse__prediction(self, word, parse_result): #parse_result is unused here
        assert set(morph.tag(word)) == set(p.tag for p in morph.parse(word))

    @with_test_data(PREFIX_PREDICTION_DATA)
    def test_tag_is_on_par_with_parse__prefix_prediction(self, word, parse_result): #parse_result is unused here
        assert set(morph.tag(word)) == set(p.tag for p in morph.parse(word))

    @with_test_data(NON_PRODUCTIVE_BUGS_DATA, 'cls')
    def test_no_nonproductive_forms(self, word, cls):
        self.assertNotTaggedAs(word, cls)


class TestParse:

    def _parsed_as(self, parse, cls):
        return any(p[1].POS==cls for p in parse)

    def _parse_cls_first_index(self, parse, cls):
        for idx, p in enumerate(parse):
            if p.tag.POS == cls:
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


class TestTagWithPrefix:

    def test_tag_with_unknown_prefix(self):
        word = 'мегакот'
        pred1 = UnknownPrefixPredictor(morph)
        pred2 = KnownPrefixPredictor(morph)

        parse1 = pred1.tag(word)
        parse2 = pred2.tag(word)
        assert parse1 == parse2


class TestUtils:
    def test_word_is_known(self):
        assert morph.dictionary.word_is_known('еж')
        assert morph.dictionary.word_is_known('ёж')
        assert not morph.dictionary.word_is_known('еш')

    def test_word_is_known_strict(self):
        assert not morph.dictionary.word_is_known('еж', strict_ee=True)
        assert morph.dictionary.word_is_known('ёж', strict_ee=True)
        assert not morph.dictionary.word_is_known('еш', strict_ee=True)


class TestParseResultClass:

    def assertNotTuples(self, parses):
        assert all(type(p) != tuple for p in parses)

    def assertAllTuples(self, parses):
        assert all(type(p) == tuple for p in parses)

    def test_namedtuples(self):
        self.assertNotTuples(morph.parse('кот'))
        self.assertNotTuples(morph.inflect('кот', set(['plur'])))
        self.assertNotTuples(morph.decline('кот'))

    def test_plain_tuples(self):
        morph_plain = pymorphy2.MorphAnalyzer(result_type=None)
        self.assertAllTuples(morph_plain.parse('кот'))
        self.assertAllTuples(morph_plain.inflect('кот', set(['plur'])))
        self.assertAllTuples(morph_plain.decline('кот'))
