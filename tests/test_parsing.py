# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import concurrent.futures
import random
import pytest
import pymorphy2
from .utils import morph


def _to_test_data(text):
    """
    Lines should be of this format: <word> <normal_form> <tag>.
    Lines that starts with "#" and blank lines are skipped.
    """
    return [l.split(None, 2) for l in text.splitlines()
            if l.strip() and not l.startswith("#")]

# TODO: lines that starts with "XFAIL" excludes the next line from testing.
PARSES = _to_test_data("""
# ========= nouns
кошка       кошка       NOUN,inan,femn sing,nomn

# ========= adjectives
хорошему            хороший     ADJF,Qual masc,sing,datv
лучший              хороший     ADJF,Supr,Qual masc,sing,nomn
наиневероятнейший   вероятный   ADJF,Supr,Qual masc,sing,nomn
наистарейший        старый      ADJF,Supr,Qual masc,sing,nomn

# ========= е/ё
котенок     котёнок     NOUN,anim,masc sing,nomn
котёнок     котёнок     NOUN,anim,masc sing,nomn
озера       озеро       NOUN,inan,neut sing,gent
озера       озеро       NOUN,inan,neut plur,nomn

# ========= particle after a hyphen
ей-то               она-то              NPRO,femn,3per sing,datv
скажи-ка            сказать-ка          VERB,perf,tran sing,impr,excl
измохратился-таки   измохратиться-таки  VERB,perf,intr masc,sing,past,indc

# ========= compound words with hyphen and immutable left
интернет-магазина       интернет-магазин    NOUN,inan,masc sing,gent
pdf-документов          pdf-документ        NOUN,inan,masc plur,gent
аммиачно-селитрового    аммиачно-селитровый ADJF,Qual masc,sing,gent
быстро-быстро           быстро-быстро       ADVB

# ========= compound words with hyphen and mutable left
команд-участниц     команда-участница   NOUN,inan,femn plur,gent
бегает-прыгает      бегать-прыгать      VERB,impf,intr sing,3per,pres,indc
дул-надувался       дуть-надуваться     VERB,impf,tran masc,sing,past,indc

# ПО- (there were bugs for such words in pymorphy 0.5.6)
почтово-банковский  почтово-банковский  ADJF masc,sing,nomn
по-прежнему         по-прежнему         ADVB

# other old bugs
поездов-экспрессов          поезд-экспресс          NOUN,inan,masc plur,gent
подростками-практикантами   подросток-практикант    NOUN,anim,masc plur,ablt
подводников-североморцев    подводник-североморец   NOUN,anim,masc plur,gent

# cities
санкт-петербурга    санкт-петербург     NOUN,inan,masc,Geox sing,gent
ростове-на-дону     ростов-на-дону      NOUN,inan,masc,Sgtm,Geox sing,loct

# ========= non-dictionary adverbs
по-западному        по-западному        ADVB
по-театральному     по-театральному     ADVB
по-воробьиному      по-воробьиному      ADVB

# ========= hyphenated words with non-cyrillic parts
# this used to raise an exception

Ретро-FM    ретро-fm    LATN

# ====================== non-words
.       .       PNCT
,       ,       PNCT
...     ...     PNCT
?!      ?!      PNCT
-       -       PNCT
…       …       PNCT

123         123         NUMB,intg
0           0           NUMB,intg
123.1       123.1       NUMB,real
123,1       123,1       NUMB,real
I           i           ROMN
MCMLXXXIX   mcmlxxxix   ROMN
XVIII       xviii       ROMN

# ========= LATN
Foo     foo     LATN
I       i       LATN

# ============== abbreviations 1
# should normal forms be expanded?

руб     руб     NOUN,inan,masc,Fixd,Abbr plur,gent
млн     млн     NOUN,inan,masc,Fixd,Abbr plur,gent
тыс     тыс     NOUN,inan,femn,Fixd,Abbr plur,gent
""")

PARSES_UPPER = [(w.upper(), norm, tag) for (w, norm, tag) in PARSES]
PARSES_TITLE = [(w.title(), norm, tag) for (w, norm, tag) in PARSES]

SYSTEMATIC_ERRORS = _to_test_data("""
# ============== foreign first names
Уилл    уилл        NOUN,anim,masc,Name sing,nomn
Джеф    джеф        NOUN,anim,masc,Name sing,nomn

# ============== last names
Сердюков    сердюков    NOUN,anim,masc,Surn sing,nomn
Третьяк     третьяк     NOUN,anim,masc,Surn sing,nomn

# ============== abbreviations 1
# should normal forms be expanded?

г       г       NOUN,inan,masc,Fixd,Abbr sing,loc2
п       п       NOUN,inan,masc,Fixd,Abbr sing,accs
ст      ст      NOUN,inan,femn,Fixd,Abbr sing,accs

# ============== abbreviations 2
# it seems is not possible to properly guess gender and number

ГКРФ        гкрф    NOUN,inan,masc,Sgtm,Fixd,Abbr sing,nomn
ПДД         пдд     NOUN,inan,neut,Pltm,Fixd,Abbr plur,nomn
ФП          фп      NOUN,inan,neut,Sgtm,Fixd,Abbr sing,nomn
ООП         ооп     NOUN,inan,neut,Sgtm,Fixd,Abbr sing,nomn
ПИН         пин     NOUN,inan,masc,Sgtm,Fixd,Abbr sing,nomn
УБРиР       убрир   NOUN,inan,masc,Abbr sing,nomn
УБРиРе      убрир   NOUN,inan,masc,Abbr sing,ablt
УБРиР-е     убрир   NOUN,inan,masc,Abbr sing,ablt

# =============== numerals
3-го        3-й     ADJF,Anum masc,sing,gent
41-й        41-й    ADJF,Anum masc,sing,nomn
41-м        41-м    ADJF,Anum masc,sing,loct
2001-й      2001-й  ADJF,Anum masc,sing,nomn
8-му        8-й     ADJF,Anum masc,sing,datv
3-х         3       NUMR,gent

уловка-22   уловка-22   NOUN,inan,femn sing,nomn

""")


def run_for_all(parses):
    return pytest.mark.parametrize(("word", "normal_form", "tag"), parses)


def assert_parse_is_correct(parse, word, normal_form, tag):
    """
    Check if one of the word parses has normal form ``normal_form``
    and tag ``tag``.
    """
    for p in parse:
        if p.normal_form == normal_form and str(p.tag) == tag:
            return
    assert False, parse


# ====== Tests:
def _test_has_parse(parses):
    @run_for_all(parses)
    def test_case(word, normal_form, tag):
        parse = morph.parse(word)
        assert_parse_is_correct(parse, word, normal_form, tag)

    return test_case

test_has_parse = _test_has_parse(PARSES)
test_has_parse_title = _test_has_parse(PARSES_TITLE)
test_has_parse_upper = _test_has_parse(PARSES_UPPER)

test_has_parse_systematic_errors = pytest.mark.xfail(_test_has_parse(SYSTEMATIC_ERRORS))


def _test_tag(parses):
    @run_for_all(parses)
    def test_tag_produces_the_same_as_parse(word, normal_form, tag):
        """
        Check if morph.tag produces the same results as morph.parse.
        """
        assert set(morph.tag(word)) == set(p.tag for p in morph.parse(word))

    return test_tag_produces_the_same_as_parse

test_tag = _test_tag(PARSES)
test_tag_title = _test_tag(PARSES_TITLE)
test_tag_upper = _test_tag(PARSES_UPPER)


def _check_analyzer(morph, parses):
    for word, normal_form, tag in parses:
        parse = morph.parse(word)
        assert_parse_is_correct(parse, word, normal_form, tag)


def _check_new_analyzer(parses):
    morph = pymorphy2.MorphAnalyzer()
    for word, normal_form, tag in parses:
        parse = morph.parse(word)
        assert_parse_is_correct(parse, word, normal_form, tag)


def _create_morph_analyzer(i):
    morph = pymorphy2.MorphAnalyzer()
    word, normal_form, tag = random.choice(PARSES)
    parse = morph.parse(word)
    assert_parse_is_correct(parse, word, normal_form, tag)


def test_threading_single_morph_analyzer():
    with concurrent.futures.ThreadPoolExecutor(3) as executor:
        res = list(executor.map(_check_analyzer, [morph]*10, [PARSES]*10))


@pytest.mark.xfail  # See https://github.com/kmike/pymorphy2/issues/37
def test_threading_multiple_morph_analyzers():
    with concurrent.futures.ThreadPoolExecutor(3) as executor:
        res = list(executor.map(_check_new_analyzer, [PARSES]*10))


@pytest.mark.xfail  # See https://github.com/kmike/pymorphy2/issues/37
def test_threading_create_analyzer():
    with concurrent.futures.ThreadPoolExecutor(3) as executor:
        res = list(executor.map(_create_morph_analyzer, range(10)))
