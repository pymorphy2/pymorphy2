# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest
from .utils import morph

LEXEMES = """\
кот кота коту кота котом коте коты котов котам котов котами котах
он его него ему нему его него им ним нём
он-то его-то него-то ему-то нему-то его-то него-то им-то ним-то нём-то
лжекот лжекота лжекоту лжекота лжекотом лжекоте лжекоты лжекотов лжекотам лжекотов лжекотами лжекотах
экс-лжекот экс-лжекота экс-лжекоту экс-лжекота экс-лжекотом экс-лжекоте экс-лжекоты экс-лжекотов экс-лжекотам экс-лжекотов экс-лжекотами экс-лжекотах
экслжекот экслжекота экслжекоту экслжекота экслжекотом экслжекоте экслжекоты экслжекотов экслжекотам экслжекотов экслжекотами экслжекотах
буропёс буропса буропсу буропса буропсом буропсе буропсы буропсов буропсам буропсов буропсами буропсах
кот-маг кота-мага коту-магу кота-мага котом-магом коте-маге коты-маги котов-магов котам-магам котов-магов котами-магами котах-магах
йотка йотки йотке йотку йоткой йоткою йотке йотки йоток йоткам йотки йотками йотках
кото-пёс кото-пса кото-псу кото-пса кото-псом кото-псе кото-псы кото-псов кото-псам кото-псов кото-псами кото-псах
кото-псевдопёс кото-псевдопса кото-псевдопсу кото-псевдопса кото-псевдопсом кото-псевдопсе кото-псевдопсы кото-псевдопсов кото-псевдопсам кото-псевдопсов кото-псевдопсами кото-псевдопсах
""".splitlines()


def _lexemes_for_word(word):
    res = []
    for p in morph.parse(word):
        res.append(tuple(f.word for f in p.lexeme))
    return res


@pytest.mark.parametrize("lexeme", LEXEMES)
def test_has_proper_lexemes(lexeme):
    lexeme_words = tuple(lexeme.split())
    variants = _lexemes_for_word(lexeme_words[0])
    if lexeme_words not in variants:
        variants_repr = "\n".join([" ".join(v) for v in variants])
        assert False, "%s not in \n%s" % (lexeme, variants_repr)


@pytest.mark.parametrize("lexeme", LEXEMES)
def test_lexemes_sanity(lexeme):
    lexeme_words = tuple(lexeme.split())

    for word in lexeme_words:
        for p in morph.parse(word):
            assert p.lexeme[0].lexeme == p.lexeme


@pytest.mark.parametrize("lexeme", LEXEMES)
def test_normalized_is_first(lexeme):
    lexeme_words = tuple(lexeme.split())
    first_parse = morph.parse(lexeme_words[0])[0]
    normal_form = (first_parse.word, first_parse.tag.POS)

    for word in lexeme_words:
        parses = morph.parse(word)
        normalized = [(p.normalized.word, p.normalized.tag.POS) for p in parses]
        assert normal_form in normalized