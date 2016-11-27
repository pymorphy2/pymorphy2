# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pickle
import pytest
import pymorphy2
from pymorphy2.units.by_lookup import DictionaryAnalyzer
from pymorphy2.units.by_analogy import UnknownPrefixAnalyzer, KnownPrefixAnalyzer
from pymorphy2.units.by_hyphen import HyphenatedWordsAnalyzer
from pymorphy2 import lang


# TODO: move most of tests to test_parsing

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
    ('иванович', ['иванович']),
    ('ивановичу', ['иванович']),

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

    ('бутявкой', ['бутявка']), # и никаких местоимений!
    ('сапают', ['сапать']), # и никаких местоимений!

    ('кюди', ['кюдить', 'кюдь', 'кюди']), # и никаких "человек"
]

NON_PRODUCTIVE_BUGS_DATA = [
    ('бякобы', 'PRCL'),
    ('бякобы', 'CONJ'),
    ('псевдоякобы', 'PRCL'),
    ('псевдоякобы', 'CONJ'),
]


def test_pickling(morph):
    data = pickle.dumps(morph, pickle.HIGHEST_PROTOCOL)
    morph2 = pickle.loads(data)
    assert morph2.tag('слово') == morph.tag('слово')


def with_test_data(data, second_param_name='parse_result'):
    return pytest.mark.parametrize(
        ("word", second_param_name),
        data
    )


class TestNormalForms:
    @with_test_data(TEST_DATA)
    def test_normal_forms(self, word, parse_result, morph):
        assert morph.normal_forms(word) == parse_result

    @with_test_data(PREDICTION_TEST_DATA)
    def test_normal_forms_prediction(self, word, parse_result, morph):
        assert morph.normal_forms(word) == parse_result

    @with_test_data(PREFIX_PREDICTION_DATA)
    def test_normal_forms_prefix_prediction(self, word, parse_result, morph):
        assert morph.normal_forms(word) == parse_result


class TestTagAndParse:
    """
    This test checks if morph.tag produces the same results as morph.parse.
    """
    def assertTagAndParseAgree(self, word, morph):
        assert set(morph.tag(word)) == set(p.tag for p in morph.parse(word))

    @with_test_data(TEST_DATA)
    def test_basic(self, word, parse_result, morph):
        self.assertTagAndParseAgree(word, morph)

    @with_test_data(PREDICTION_TEST_DATA)
    def test_prediction(self, word, parse_result, morph):
        self.assertTagAndParseAgree(word, morph)

    @with_test_data(PREFIX_PREDICTION_DATA)
    def test_prefix_prediction(self, word, parse_result, morph):
        self.assertTagAndParseAgree(word, morph)


class TestTagMethod:
    def _tagged_as(self, tags, cls):
        return any(tag.POS == cls for tag in tags)

    def assertNotTaggedAs(self, word, cls, morph):
        tags = morph.tag(word)
        assert not self._tagged_as(tags, cls), (tags, cls)

    @with_test_data(NON_PRODUCTIVE_BUGS_DATA, 'cls')
    def test_no_nonproductive_forms(self, word, cls, morph):
        self.assertNotTaggedAs(word, cls, morph)


class TestParse:
    def _parsed_as(self, parse, cls):
        return any(p[1].POS==cls for p in parse)

    def _parse_cls_first_index(self, parse, cls):
        for idx, p in enumerate(parse):
            if p.tag.POS == cls:
                return idx

    def assertNotParsedAs(self, word, cls, morph):
        parse = morph.parse(word)
        assert not self._parsed_as(parse, cls), (parse, cls)

    @with_test_data(NON_PRODUCTIVE_BUGS_DATA, 'cls')
    def test_no_nonproductive_forms(self, word, cls, morph):
        self.assertNotParsedAs(word, cls, morph)

    def test_no_duplicate_parses(self, morph):
        parse = morph.parse('бутявкой')
        data = [variant[:3] for variant in parse]
        assert len(set(data)) == len(data), parse

    def test_parse_order(self, morph):
        parse = morph.parse('продюсерство')
        assert self._parsed_as(parse, 'NOUN')
        assert self._parsed_as(parse, 'ADVB')
        assert self._parse_cls_first_index(parse, 'NOUN') < self._parse_cls_first_index(parse, 'ADVB')


class TestHyphen:
    def assert_not_parsed_by_hyphen(self, word, morph):
        for p in morph.parse(word):
            for meth in p.methods_stack:
                analyzer = meth[0]
                assert not isinstance(analyzer, HyphenatedWordsAnalyzer), p.methods_stack

    def test_no_hyphen_analyzer_for_known_prefixes(self, morph):
        # this word should be parsed by KnownPrefixAnalyzer
        self.assert_not_parsed_by_hyphen('мини-будильник', morph)

    def test_no_hyphen_analyzer_bad_input(self, morph):
        self.assert_not_parsed_by_hyphen('привет-пока-', morph)


class TestTagWithPrefix:
    def test_tag_with_unknown_prefix(self, morph):
        word = 'мегакот'

        pred1 = UnknownPrefixAnalyzer()
        pred1.init(morph)
        pred2 = KnownPrefixAnalyzer(lang.ru.KNOWN_PREFIXES)
        pred2.init(morph)

        parse1 = pred1.tag(word, word.lower(), set())
        parse2 = pred2.tag(word, word.lower(), set())
        assert parse1 == parse2

    def test_longest_prefixes_are_used(self, morph):
        parses = morph.parse('недобарабаном')
        assert len(parses) == 1
        assert len(parses[0].methods_stack) == 2 # недо+барабаном, not не+до+барабаном


class TestUtils:
    def test_word_is_known(self, morph):
        assert morph.word_is_known('еж')
        assert morph.word_is_known('ёж')
        assert not morph.word_is_known('еш')

    def test_word_is_known_strict(self, morph):
        assert not morph.word_is_known('еж', strict=True)
        assert morph.word_is_known('ёж', strict=True)
        assert not morph.word_is_known('еш', strict=True)


class TestParseResultClass:
    def assertNotTuples(self, parses):
        assert all(type(p) != tuple for p in parses)

    def assertAllTuples(self, parses):
        assert all(type(p) == tuple for p in parses)

    def test_namedtuples(self, morph):
        self.assertNotTuples(morph.parse('кот'))
        # self.assertNotTuples(morph.inflect('кот', set(['plur'])))
        # self.assertNotTuples(morph.decline('кот'))

    def test_plain_tuples(self):
        morph_plain = pymorphy2.MorphAnalyzer(result_type=None)
        self.assertAllTuples(morph_plain.parse('кот'))
        # self.assertAllTuples(morph_plain.inflect('кот', set(['plur'])))
        # self.assertAllTuples(morph_plain.decline('кот'))


class TestLatinPredictor:
    def test_tag(self, morph):
        assert morph.tag('Maßstab') == [morph.TagClass('LATN')]

    def test_parse(self, morph):
        parses = morph.parse('Maßstab')
        assert len(parses) == 1
        assert 'LATN' in parses[0].tag

    def test_lexeme(self, morph):
        p = morph.parse('Maßstab')[0]
        assert p.lexeme == [p]

    def test_normalized(self, morph):
        p = morph.parse('Maßstab')[0]
        assert p.normalized == p

    def test_normal_forms(self, morph):
        assert morph.normal_forms('Maßstab') == ['maßstab']


class TetsPunctuationPredictor:
    def test_tag(self, morph):
        assert morph.tag('…') == [morph.TagClass('PNCT')]


class TestInitials:
    def assertHasFirstName(self, tags):
        assert any(set(['Name', 'Abbr']) in tag for tag in tags), tags

    def assertHasPatronymic(self, tags):
        assert any(set(['Patr', 'Abbr']) in tag for tag in tags), tags

    def _filter_parse(self, word, grammemes, morph):
        return [p for p in morph.parse(word) if set(grammemes) in p.tag]

    def test_tag(self, morph):
        tags = morph.tag('Д')
        self.assertHasFirstName(tags)
        self.assertHasPatronymic(tags)

    def test_tag_conj(self, morph):
        tags = morph.tag('И')
        self.assertHasFirstName(tags)
        self.assertHasPatronymic(tags)
        assert any('CONJ' in tag for tag in tags), tags

    def test_parse(self, morph):
        tags = [p.tag for p in morph.parse('И')]
        self.assertHasFirstName(tags)
        self.assertHasPatronymic(tags)

    def test_normalize_name_masc(self, morph):
        parse = self._filter_parse('И', ['Name', 'accs', 'masc'], morph)[0]
        assert parse.normalized.word == 'и'
        assert parse.normalized.tag.case == 'nomn'
        assert parse.normalized.tag.gender == 'masc'

    def test_normalize_patr_masc(self, morph):
        parse = self._filter_parse('И', ['Patr', 'accs', 'masc'], morph)[0]
        assert parse.normalized.word == 'и'
        assert parse.normalized.tag.case == 'nomn'
        assert parse.normalized.tag.gender == 'masc'

    def test_normalize_name_femn(self, morph):
        parse = self._filter_parse('И', ['Name', 'accs', 'femn'], morph)[0]
        assert parse.normalized.word == 'и'
        assert parse.normalized.tag.case == 'nomn'
        assert parse.normalized.tag.gender == 'femn'

    def test_normalize_patr_femn(self, morph):
        parse = self._filter_parse('И', ['Patr', 'accs', 'femn'], morph)[0]
        assert parse.normalized.word == 'и'
        assert parse.normalized.tag.case == 'nomn'
        assert parse.normalized.tag.gender == 'masc'


def test_iter_known_word_parses(morph):
    parses = list(morph.iter_known_word_parses('приве'))
    assert any(
        (p.word=='привет' and isinstance(p.methods_stack[0][0], DictionaryAnalyzer))
        for p in parses
    ), parses
