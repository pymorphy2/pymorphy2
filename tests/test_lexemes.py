# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest
from .utils import morph

# lexemes are divided by blank lines;
# lines that starts with "#" are comments;
# lines that starts with "XFAIL" excludes lexeme from testing.
LEXEMES = """
# =========== noun
кот кота коту кота котом коте
коты котов котам котов котами котах

# =========== pronoun
он его него ему нему его него
им ним нём

# =========== pronoun with a particle
он-то его-то него-то ему-то нему-то его-то него-то
им-то ним-то нём-то

# =========== noun with a known prefix
лжекот лжекота лжекоту лжекота лжекотом лжекоте
лжекоты лжекотов лжекотам лжекотов лжекотами лжекотах

# =========== noun with two known prefixes (hyphenated)
экс-лжекот экс-лжекота экс-лжекоту экс-лжекота экс-лжекотом экс-лжекоте
экс-лжекоты экс-лжекотов экс-лжекотам экс-лжекотов экс-лжекотами экс-лжекотах

# =========== noun with two knoen prefixes
экслжекот экслжекота экслжекоту экслжекота экслжекотом экслжекоте экслжекоты
экслжекотов экслжекотам экслжекотов экслжекотами экслжекотах

# =========== noun witn a guessed prefix
буропёс буропса буропсу буропса буропсом буропсе
буропсы буропсов буропсам буропсов буропсами буропсах

# =========== both parts can be inflected the same way
кот-маг кота-мага коту-магу кота-мага котом-магом коте-маге
коты-маги котов-магов котам-магам котов-магов котами-магами котах-магах

команда-участница команды-участницы команде-участнице команду-участницу командой-участницей командою-участницею команде-участнице
команды-участницы команд-участниц командам-участницам команды-участниц командами-участницами командах-участницах

# =========== prediction using suffix
йотка йотки йотке йотку йоткой йоткою йотке
йотки йоток йоткам йотки йотками йотках

# =========== left part is fixed
кото-пёс кото-пса кото-псу кото-пса кото-псом кото-псе
кото-псы кото-псов кото-псам кото-псов кото-псами кото-псах

# =========== left part is fixed, right is with known prefix
кото-псевдопёс кото-псевдопса кото-псевдопсу кото-псевдопса кото-псевдопсом кото-псевдопсе
кото-псевдопсы кото-псевдопсов кото-псевдопсам кото-псевдопсов кото-псевдопсами кото-псевдопсах

# =========== numeral with gender
два двух двум два двух двумя двух
две двух двум две двух двумя двух
два двух двум два двумя двух

# =========== two adverbs
красиво-туманно

# =========== adverb ПО-..
по-театральному

по-западному

# =========== two numerals: one depends on gender, the other doesn't
XFAIL: see https://github.com/kmike/pymorphy2/issues/18
два-три двух-трёх двум-трем два-три двух-трёх двумя-тремя двух-трёх
две-три двух-трёх двум-трем две-три двух-трёх двумя-тремя двух-трёх
два-три двух-трёх двум-трём два-три двумя-тремя двух-трёх

# =========== two nouns that parses differently
человек-гора человека-горы человеку-горе человека-гору человеком-горой человеком-горою человеке-горе
люди-горы людей-гор людям-горам людей-горы людьми-горами людях-горах

гора-человек горы-человека горе-человеку гору-человека горой-человеком горе-человеке
горы-люди гор-людей гор-человек горам-людям горам-человекам горы-людей горами-людьми горами-человеками горах-людях горах-человеках

XFAIL: this is currently too complex
человек-гора человека-горы человеку-горе человека-гору человеком-горой человеком-горою человеке-горе
люди-горы людей-гор человек-гор людям-горам человекам-горам людей-гор людьми-горами человеками-горами людях-горах человеках-горах

# =========== two nouns, one of which has gen1/gen2 forms
лес-колдун леса-колдуна лесу-колдуну лес-колдуна лесом-колдуном лесе-колдуне
леса-колдуны лесов-колдунов лесам-колдунам леса-колдунов лесами-колдунами лесах-колдунах

""".strip()

LEXEMES = "".join(l for l in LEXEMES.splitlines(True) if not l.startswith("#")).split("\n\n")


def _parse_lexeme(lexeme):
    lexeme_words = tuple(lexeme.split())
    if lexeme_words[0].startswith('XFAIL'):
        pytest.xfail()
    return lexeme_words


# ============ Tests:

@pytest.mark.parametrize("lexeme", LEXEMES)
def test_has_proper_lexemes(lexeme):
    """
    Check if the lexeme of first word in the lexeme is the same lexeme.
    """
    lexeme_words = _parse_lexeme(lexeme)

    variants = _lexemes_for_word(lexeme_words[0])
    if lexeme_words not in variants:
        variants_repr = "\n".join([" ".join(v) for v in variants])
        assert False, "%s not in \n%s" % (lexeme, variants_repr)


@pytest.mark.parametrize("lexeme", LEXEMES)
def test_lexemes_sanity(lexeme):
    """
    Check if parse.lexeme works properly by applying it several times.
    """
    lexeme_words = _parse_lexeme(lexeme)

    for word in lexeme_words:
        for p in morph.parse(word):
            assert p.lexeme[0].lexeme == p.lexeme


@pytest.mark.parametrize("lexeme", LEXEMES)
def test_normalized_is_first(lexeme):
    """
    Test that parse.normalized is a first form in lexeme.
    """
    lexeme_words = _parse_lexeme(lexeme)

    first_parse = morph.parse(lexeme_words[0])[0]
    normal_form = (first_parse.word, first_parse.tag.POS)

    for word in lexeme_words:
        parses = morph.parse(word)
        normalized = [(p.normalized.word, p.normalized.tag.POS) for p in parses]
        assert normal_form in normalized

def _lexemes_for_word(word):
    res = []
    for p in morph.parse(word):
        res.append(tuple(f.word for f in p.lexeme))
    return res

