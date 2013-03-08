# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest
from .utils import morph

# Lines should be of this format: <word> <normal_form> <tag>.
# Lines that starts with "#" and blank lines are skipped;
# TODO: lines that starts with "XFAIL" excludes the next line from testing.
PARSES = """
# ========= particle after a hyphen:
ей-то               она-то              NPRO,femn,3per sing,datv
скажи-ка            сказать-ка          VERB,perf,tran sing,impr,excl
измохратился-таки   измохратиться-таки  VERB,perf,intr masc,sing,past,indc

# ========= compound words with hyphen and immutable left:
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

# ========= non-dictionary adverbs:
по-западному        по-западному        ADVB
по-театральному     по-театральному     ADVB
по-воробьиному      по-воробьиному      ADVB

""".splitlines()

PARSES = [l.split(None, 2) for l in PARSES if l.strip() and not l.startswith("#")]

def run_for_all(parses):
    return pytest.mark.parametrize(("word", "normal_form", "tag"), parses)

# ====== Tests:

@run_for_all(PARSES)
def test_has_parse(word, normal_form, tag):
    """
    Check if one of the word parses has normal form ``normal_form``
    and tag ``tag``.
    """
    for p in morph.parse(word):
        if p.normal_form == normal_form and str(p.tag) == tag:
            return

    assert False, morph.parse(word)


@run_for_all(PARSES)
def test_tag_produces_the_same_as_parse(word, normal_form, tag):
    """
    Check if morph.tag produces the same results as morph.parse.
    """
    assert set(morph.tag(word)) == set(p.tag for p in morph.parse(word))
