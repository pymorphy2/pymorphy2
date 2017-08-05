# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import random
import concurrent.futures
import pytest
import pymorphy2
from utils import assert_parse_is_correct


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
ей-то               она-то              NPRO,femn,3per,Anph sing,datv
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

# issue with normal form caching
залом   зал     NOUN,inan,masc sing,ablt

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

# ========= UNKN
ьё      ьё      UNKN

# ============== common lowercased abbreviations

руб     руб     NOUN,inan,masc,Fixd,Abbr plur,gent
млн     млн     NOUN,inan,masc,Fixd,Abbr plur,gent
тыс     тыс     NOUN,inan,femn,Fixd,Abbr plur,gent
ст      ст      NOUN,inan,femn,Fixd,Abbr sing,accs
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

# ============== common lowercased abbreviations
# should normal forms be expanded?

г       г       NOUN,inan,masc,Fixd,Abbr sing,loc2
п       п       NOUN,inan,masc,Fixd,Abbr sing,accs

# ============== uppercased abbreviations
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


# ====== Tests:
def _test_has_parse(parses):
    @run_for_all(parses)
    def test_case(word, normal_form, tag, morph):
        parse = morph.parse(word)
        assert_parse_is_correct(parse, word, normal_form, tag)

    return test_case

test_has_parse = _test_has_parse(PARSES)
test_has_parse_title = _test_has_parse(PARSES_TITLE)
test_has_parse_upper = _test_has_parse(PARSES_UPPER)

test_has_parse_systematic_errors = pytest.mark.xfail(_test_has_parse(SYSTEMATIC_ERRORS))


def _test_tag(parses):
    @run_for_all(parses)
    def test_tag_produces_the_same_as_parse(word, normal_form, tag, morph):
        """
        Check if morph.tag produces the same results as morph.parse.
        """
        assert set(morph.tag(word)) == set(p.tag for p in morph.parse(word))

    return test_tag_produces_the_same_as_parse

test_tag = _test_tag(PARSES)
test_tag_title = _test_tag(PARSES_TITLE)
test_tag_upper = _test_tag(PARSES_UPPER)
