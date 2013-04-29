# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest

from .utils import morph


@pytest.mark.parametrize(('word', 'result'), [
    # прилагательные
    ("бесплатная", ["бесплатная", "бесплатные", "бесплатных"]),
    ("бесплатный", ["бесплатный", "бесплатных", "бесплатных"]),
    
    # числительные
    ("первый", ["первый", "первых", "первых"]),
    ("первая", ["первая", "первые", "первых"]),

    # существительные
    ("книга", ["книга", "книги", "книг"]),
    ("болт", ["болт", "болта", "болтов"]),

    # причастия
    ("летящий", ["летящий", "летящих", "летящих"]),
    ("летящая", ["летящая", "летящие", "летящих"]),

    # глаголы
    ("играет", ["играет", "играют", "играют"]),
    ("играл", ["играл", "играли", "играли"]),
])
def test_plural_forms(word, result):
    parsed = morph.parse(word)
    assert len(parsed)
    for plural, num in zip(result, [1, 2, 5]):
        assert parsed[0].make_agree_with_number(num).word == plural


@pytest.mark.parametrize(('word', 'case', 'result'), [
    ("книги", 'gent', ["книги", "книг", "книг"]),
    ("книге", 'datv', ["книге", "книгам", "книгам"]),
    ("книгу", 'accs', ["книгу", "книги", "книг"]),
    ("книгой", 'ablt', ["книгой", "книгами", "книгами"]),
    ("книге", 'loct', ["книге", "книгах", "книгах"]),
])
def test_plural_inflected(word, case, result):
    parsed = [p for p in morph.parse(word) if p.tag.case == case]
    assert len(parsed)
    for plural, num in zip(result, [1, 2, 5]):
        assert parsed[0].make_agree_with_number(num).word == plural


@pytest.mark.parametrize(('word', 'num', 'result'), [
    ("лопата", 0, "лопат"),
    ("лопата", 1, "лопата"),
    ("лопата", 2, "лопаты"),
    ("лопата", 4, "лопаты"),
    ("лопата", 5, "лопат"),
    ("лопата", 6, "лопат"),
    ("лопата", 11, "лопат"),
    ("лопата", 12, "лопат"),
    ("лопата", 15, "лопат"),
    ("лопата", 21, "лопата"),
    ("лопата", 24, "лопаты"),
    ("лопата", 25, "лопат"),
    ("лопата", 101, "лопата"),
    ("лопата", 103, "лопаты"),
    ("лопата", 105, "лопат"),
    ("лопата", 111, "лопат"),
    ("лопата", 112, "лопат"),
    ("лопата", 151, "лопата"),
    ("лопата", 122, "лопаты"),
    ("лопата", 5624, "лопаты"),
    ("лопата", 5431, "лопата"),
    ("лопата", 7613, "лопат"),
    ("лопата", 2111, "лопат"),
])
def test_plural_num(word, num, result):
    parsed = morph.parse(word)
    assert len(parsed)
    assert parsed[0].make_agree_with_number(num).word == result
