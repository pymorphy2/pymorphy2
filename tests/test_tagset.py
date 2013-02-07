# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest

from pymorphy2.tagset import OpencorporaTag
from .utils import morph

def test_hashing():
    tag1 = OpencorporaTag('NOUN')
    tag2 = OpencorporaTag('NOUN')
    tag3 = OpencorporaTag('VERB')

    assert tag1 == tag2
    assert tag1 != tag3
    assert set([tag1]) == set([tag2])
    assert set([tag3]) != set([tag1])


@pytest.mark.parametrize(("tag", "cls"), [
        ['NOUN', 'NOUN'],
        ['NOUN,sing', 'NOUN'],
        ['NOUN sing', 'NOUN'],
    ])
def test_cls(tag, cls):
    assert OpencorporaTag(tag).POS == cls

def test_repr():
    assert repr(OpencorporaTag('NOUN anim,plur')) == "OpencorporaTag('NOUN anim,plur')"


class TestUpdated:

    def test_number(self):
        tag = OpencorporaTag('NOUN,sing,masc')
        grammemes = tag.updated_grammemes(required=set(['plur']))
        assert grammemes == set(['NOUN', 'plur'])

    def test_order(self):
        tag = OpencorporaTag('VERB,impf,tran sing,3per,pres,indc')
        grammemes = tag.updated_grammemes(required=set(['1per']))
        assert grammemes == set('VERB,sing,impf,tran,1per,pres,indc'.split(','))


class TestAttributes:

    def test_attributes(self):
        tag = OpencorporaTag('VERB,impf,tran sing,3per,pres,indc')
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

    def test_attributes2(self):
        tag = OpencorporaTag('NOUN,inan,masc plur,accs')
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

    def test_attributes3(self):
        tag = OpencorporaTag('PRTF,impf,tran,pres,pssv inan,masc,sing,accs')
        assert tag.voice == 'pssv'

    def test_attributes4(self):
        tag = OpencorporaTag('VERB,perf,tran plur,impr,excl')
        assert tag.involvement == 'excl'


class TestContains:

    def test_contains_correct(self):
        tag_text = 'VERB,perf,tran plur,impr,excl'
        tag = OpencorporaTag(tag_text)
        for grammeme in tag_text.replace(' ', ',').split(','):
            assert grammeme in tag

    def test_not_contains(self):
        # we need to use a prepared Tag class for this to work
        Tag = morph.tag_class()
        tag = Tag('VERB,perf,tran plur,impr,excl')

        assert 'VERB' in tag
        assert 'NOUN' not in tag
        assert 'sing' not in tag
        assert 'Dist' not in tag

    def test_contains_error(self):
        # we need to use a prepared Tag class for this to work
        Tag = morph.tag_class()
        tag = Tag('VERB,perf,tran plur,impr,excl')

        with pytest.raises(ValueError):
            assert 'foo' in tag

        with pytest.raises(ValueError):
            assert 'VERP' in tag
