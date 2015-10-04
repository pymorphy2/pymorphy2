# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pickle
import pytest

import pymorphy2
from pymorphy2.tagset import OpencorporaTag


def test_hashing(Tag):
    tag1 = Tag('NOUN')
    tag2 = Tag('NOUN')
    tag3 = Tag('VERB')

    assert tag1 == tag2
    assert tag1 != tag3
    assert set([tag1]) == set([tag2])
    assert set([tag3]) != set([tag1])


@pytest.mark.parametrize(("tag", "cls"), [
        ['NOUN', 'NOUN'],
        ['NOUN,sing', 'NOUN'],
        ['NOUN sing', 'NOUN'],
    ])
def test_cls(tag, cls, Tag):
    assert Tag(tag).POS == cls


def test_repr(Tag):
    assert repr(Tag('NOUN anim,plur')) == "OpencorporaTag('NOUN anim,plur')"


# Cloning of the Tag class is disabled to allow pickling
@pytest.mark.xfail
def test_extra_grammemes(Tag):
    m = pymorphy2.MorphAnalyzer()

    assert m.TagClass.KNOWN_GRAMMEMES is not Tag.KNOWN_GRAMMEMES
    assert m.TagClass.KNOWN_GRAMMEMES is not OpencorporaTag.KNOWN_GRAMMEMES

    assert 'new_grammeme' not in Tag.KNOWN_GRAMMEMES
    assert 'new_grammeme' not in m.TagClass.KNOWN_GRAMMEMES

    m.TagClass.KNOWN_GRAMMEMES.add('new_grammeme')

    new_tag = m.TagClass('NOUN,sing,new_grammeme')

    assert 'new_grammeme' in new_tag
    assert 'new_grammeme' in m.TagClass.KNOWN_GRAMMEMES
    assert 'new_grammeme' not in OpencorporaTag.KNOWN_GRAMMEMES
    assert 'new_grammeme' not in Tag.KNOWN_GRAMMEMES


def test_len(Tag):
    assert len(Tag('NOUN')) == 1
    assert len(Tag('NOUN plur')) == 2
    assert len(Tag('NOUN plur,masc')) == 3
    assert len(Tag('NOUN,plur,masc')) == 3


def test_pickle(Tag):
    tag = Tag('NOUN')
    data = pickle.dumps(tag, pickle.HIGHEST_PROTOCOL)
    tag_unpickled = pickle.loads(data)
    assert tag == tag_unpickled


def test_pickle_custom():
    m = pymorphy2.MorphAnalyzer()
    m.TagClass.KNOWN_GRAMMEMES.add('new_grammeme')
    tag = m.TagClass('new_grammeme')
    data = pickle.dumps(tag, pickle.HIGHEST_PROTOCOL)
    tag_unpickled = pickle.loads(data)
    assert tag == tag_unpickled


class TestUpdated:

    def test_number(self, Tag):
        tag = Tag('NOUN,sing,masc')
        grammemes = tag.updated_grammemes(required=set(['plur']))
        assert grammemes == set(['NOUN', 'plur'])

    def test_order(self, Tag):
        tag = Tag('VERB,impf,tran sing,3per,pres,indc')
        grammemes = tag.updated_grammemes(required=set(['1per']))
        assert grammemes == set('VERB,sing,impf,tran,1per,pres,indc'.split(','))


class TestAttributes:

    def test_attributes(self, Tag):
        tag = Tag('VERB,impf,tran sing,3per,pres,indc')
        assert tag.POS == 'VERB'
        assert tag.gender is None
        assert tag.animacy is None
        assert tag.number == 'sing'
        assert tag.case is None
        assert tag.tense == 'pres'
        assert tag.aspect == 'impf'
        assert tag.mood == 'indc'
        assert tag.person == '3per'
        assert tag.transitivity == 'tran'
        assert tag.voice is None # ?
        assert tag.involvement is None

    def test_attributes2(self, Tag):
        tag = Tag('NOUN,inan,masc plur,accs')
        assert tag.POS == 'NOUN'
        assert tag.gender == 'masc'
        assert tag.animacy == 'inan'
        assert tag.number == 'plur'
        assert tag.case == 'accs'
        assert tag.tense is None
        assert tag.aspect is None
        assert tag.mood is None
        assert tag.person is None
        assert tag.transitivity is None
        assert tag.voice is None
        assert tag.involvement is None

    def test_attributes3(self, Tag):
        tag = Tag('PRTF,impf,tran,pres,pssv inan,masc,sing,accs')
        assert tag.voice == 'pssv'

    def test_attributes4(self, Tag):
        tag = Tag('VERB,perf,tran plur,impr,excl')
        assert tag.involvement == 'excl'

    def test_attribute_exceptions(self, Tag):
        tag = Tag('NOUN,inan,masc plur,accs')

        with pytest.raises(ValueError):
            tag.POS == 'hello'

        with pytest.raises(ValueError):
            tag.POS == 'noun'

    def test_attributes_as_set_items(self, Tag):
        tag = Tag('NOUN,inan,masc plur,accs')

        # this doesn't raise an exception
        assert tag.gender in set(['masc', 'sing'])


class TestContains:

    def test_contains_correct(self, Tag):
        tag_text = 'VERB,perf,tran plur,impr,excl'
        tag = Tag(tag_text)
        for grammeme in tag_text.replace(' ', ',').split(','):
            assert grammeme in tag

    def test_not_contains(self, Tag):
        # we need to use a prepared Tag class for this to work
        tag = Tag('VERB,perf,tran plur,impr,excl')

        assert 'VERB' in tag
        assert 'NOUN' not in tag
        assert 'sing' not in tag
        assert 'Dist' not in tag

    def test_contains_error(self, Tag):
        # we need to use a prepared Tag class for this to work
        tag = Tag('VERB,perf,tran plur,impr,excl')

        with pytest.raises(ValueError):
            assert 'foo' in tag

        with pytest.raises(ValueError):
            assert 'VERP' in tag

    def test_contains_set(self, Tag):
        tag = Tag('VERB,perf,tran plur,impr,excl')
        assert set(['VERB', 'perf']) in tag
        assert set(['VERB', 'sing']) not in tag

        assert set() in tag # ??

        with pytest.raises(ValueError):
            assert set(['VERB', 'pref']) in tag


class TestCyrillic:
    def test_cyr_repr(self, Tag):
        tag = Tag('VERB,perf,tran plur,impr,excl')
        assert tag.cyr_repr == 'ГЛ,сов,перех мн,повел,выкл'

    def test_grammemes_cyr(self, Tag):
        tag = Tag('VERB,perf,tran plur,impr,excl')
        assert tag.grammemes_cyr == frozenset(['ГЛ','сов','перех', 'мн','повел','выкл'])

    def test_cyr_extra_grammemes(self, Tag):
        tag = Tag('ROMN')
        assert tag.cyr_repr == 'РИМ'

    @pytest.mark.parametrize(('lat', 'cyr'), [
        ('VERB,perf,tran plur,impr,excl', 'ГЛ,сов,перех мн,повел,выкл'),
        ('ROMN', 'РИМ'),
        ('ROMN,unknown_grammeme', 'РИМ,unknown_grammeme'),
        ('plur', 'мн'),
    ])
    def test_lat2cyr(self, lat, cyr, Tag, morph):
        assert Tag.lat2cyr(lat) == cyr
        assert Tag.cyr2lat(cyr) == lat
        assert morph.lat2cyr(lat) == cyr
        assert morph.cyr2lat(cyr) == lat
