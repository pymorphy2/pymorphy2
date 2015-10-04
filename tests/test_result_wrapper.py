# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

def test_indexing(morph):
    assert len(morph.parse('стреляли')) == 1
    p = morph.parse('стреляли')[0]

    assert p[0] == 'стреляли' # word
    assert p[1].POS == 'VERB' # tag
    assert p[2] == 'стрелять'

    assert p[0] == p.word
    assert p[1] == p.tag
    assert p[2] == p.normal_form


def test_inflect_valid(morph):
    p = morph.parse('стреляли')[0]
    assert p.inflect(set(['femn'])).word == 'стреляла'


def test_inflect_invalid(morph):
    p = morph.parse('стреляли')[0]
    assert p.inflect(set(['NOUN'])) == None


def test_is_known(morph):
    assert morph.parse('стреляли')[0].is_known
    assert not morph.parse('сптриояли')[0].is_known


def test_normalized(morph):
    assert morph.parse('стреляли')[0].normalized.word == 'стрелять'
