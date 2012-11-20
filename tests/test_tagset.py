# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest

from pymorphy2.tagset import OpencorporaTag

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
    assert OpencorporaTag(tag).cls == cls

def test_repr():
    assert repr(OpencorporaTag('NOUN anim,plur')) == "OpencorporaTag('NOUN anim,plur')"


class TestUpdated(object):

    def test_number(self):
        tag = OpencorporaTag('NOUN,sing,masc')
        assert OpencorporaTag('NOUN,plur') == tag._updated(add=['plur'])

    def test_order(self):
        tag = OpencorporaTag('VERB,impf,tran sing,3per,pres,indc')
        assert str(tag._updated(['1per'])) == 'VERB sing,impf,tran,1per,pres,indc'