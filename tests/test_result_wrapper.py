# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .utils import morph

def test_indexing():
    assert len(morph.parse('стреляли')) == 1
    p = morph.parse('стреляли')[0]

    assert p[0] == 'стреляли' # word
    assert p[1].POS == 'VERB' # tag
    assert p[2] == 'стрелять'

    assert p[0] == p.word
    assert p[1] == p.tag
    assert p[2] == p.normal_form

def test_inflect_valid():
    p = morph.parse('стреляли')[0]
    assert p.inflect(set(['femn'])).word == 'стреляла'

def test_inflect_invalid():
    p = morph.parse('стреляли')[0]
    assert p.inflect(set(['NOUN'])) == None


def test_is_known():
    assert morph.parse('стреляли')[0].is_known
    assert not morph.parse('сптриояли')[0].is_known

def test_normalized():
    assert morph.parse('стреляли')[0].normalized.word == 'стрелять'

def test_lexeme():
    parses = morph.parse('кот')
    assert len(parses) == 1

    forms = [p.word for p in parses[0].lexeme]
    assert forms == ['кот', 'кота', 'коту', 'кота', 'котом', 'коте',
                     'коты', 'котов', 'котам', 'котов', 'котами', 'котах']



