# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest

from .utils import morph
from pymorphy2.tagset import OpencorporaTag


@pytest.mark.parametrize(('word', 'tag'), [
    (u'22-ой', set([
        OpencorporaTag('ADJF,Qual femn,sing,gent'),
        OpencorporaTag('ADJF,Qual femn,sing,datv'),
        OpencorporaTag('ADJF,Qual femn,sing,ablt'),
        OpencorporaTag('ADJF,Qual femn,sing,loct'),
        OpencorporaTag('ADJF masc,sing,nomn'),
        OpencorporaTag('ADJF inan,masc,sing,accs'),
        OpencorporaTag('ADJF femn,sing,gent'),
        OpencorporaTag('ADJF femn,sing,datv'),
        OpencorporaTag('ADJF femn,sing,ablt'),
        OpencorporaTag('ADJF femn,sing,loct')]),
    ),
])
def test_numb(word, tag):
    assert set(morph.tag(word)) == tag
