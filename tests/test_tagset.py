# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest

from pymorphy2.tagset import OpencorporaTag

def test_hashing():
    tag1 = OpencorporaTag('NOUN')
    tag2 = OpencorporaTag('NOUN')

    assert set([tag1]) == set([tag2])


@pytest.mark.parametrize(("tag", "cls"), [
        ['NOUN', 'NOUN'],
        ['NOUN,sing', 'NOUN'],
        ['NOUN sing', 'NOUN'],
    ])
def test_cls(tag, cls):
    assert OpencorporaTag(tag).get_class() == cls


