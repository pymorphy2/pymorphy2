# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest
from .utils import morph

LEXEMES = """\
кот кота коту кота котом коте коты котов котам котов котами котах
он его него ему нему его него им ним нём
он-то его-то него-то ему-то нему-то его-то него-то им-то ним-то нём-то
экс-лжекот экс-лжекота экс-лжекоту экс-лжекота экс-лжекотом экс-лжекоте экс-лжекоты экс-лжекотов экс-лжекотам экс-лжекотов экс-лжекотами экс-лжекотах
лжекот лжекота лжекоту лжекота лжекотом лжекоте лжекоты лжекотов лжекотам лжекотов лжекотами лжекотах
"""


def _lexeme_variants(word):
    res = set()
    for p in morph.parse(word):
        res.add(tuple(f.word for f in p.lexeme))
    return res


@pytest.mark.parametrize("lexeme", LEXEMES.splitlines())
def test_has_lexemes(lexeme):
    lexeme_words = tuple(lexeme.split())
    for word in lexeme_words:
        variants = _lexeme_variants(word)
        if lexeme_words not in variants:
            for v in variants:
                print(" ".join(v))
            assert False
