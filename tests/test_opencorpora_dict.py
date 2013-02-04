# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from pymorphy2.opencorpora_dict.compile import _to_paradigm

class TestToParadigm(object):

    def test_simple(self):
        lexeme = [
            ["ярче", "COMP,Qual"],
            ["ярчей", "COMP,Qual V-ej"],
        ]
        stem, forms = _to_paradigm(lexeme)
        assert stem == "ярче"
        assert forms == (
            ("", "COMP,Qual", ""),
            ("й", "COMP,Qual V-ej", ""),
        )

    def test_single_prefix(self):
        lexeme = [
            ["ярче", "COMP,Qual"],
            ["поярче", "COMP,Qual Cmp2"],
        ]
        stem, forms = _to_paradigm(lexeme)
        assert stem == "ярче"
        assert forms == (
            ("", "COMP,Qual", ""),
            ("", "COMP,Qual Cmp2", "по"),
        )

    def test_multiple_prefixes(self):
        lexeme = [
            ["ярче", "COMP,Qual"],
            ["ярчей", "COMP,Qual V-ej"],
            ["поярче", "COMP,Qual Cmp2"],
            ["поярчей", "COMP,Qual Cmp2,V-ej"],
            ["наиярчайший", "ADJF,Supr,Qual masc,sing,nomn"],
        ]
        stem, forms = _to_paradigm(lexeme)
        assert stem == 'ярч'

    def test_multiple_prefixes_2(self):
        lexeme = [
            ["подробнейший", 1],
            ["наиподробнейший", 2],
            ["поподробнее", 3]
        ]
        stem, forms = _to_paradigm(lexeme)
        assert stem == 'подробне'
        assert forms == (
            ("йший", 1, ""),
            ("йший", 2, "наи"),
            ("е", 3, "по"),
        )

    def test_platina(self):
        lexeme = [
            ["платиновее", 1],
            ["платиновей", 2],
            ["поплатиновее", 3],
            ["поплатиновей", 4],
        ]
        stem, forms = _to_paradigm(lexeme)
        assert forms == (
            ("е", 1, ""),
            ("й", 2, ""),
            ("е", 3, "по"),
            ("й", 4, "по"),
        )
        assert stem == 'платинове'

    def test_no_prefix(self):
        lexeme = [["английский", 1], ["английского", 2]]
        stem, forms = _to_paradigm(lexeme)
        assert stem == 'английск'
        assert forms == (
            ("ий", 1, ""),
            ("ого", 2, ""),
        )

    def test_single(self):
        lexeme = [["английски", 1]]
        stem, forms = _to_paradigm(lexeme)
        assert stem == 'английски'
        assert forms == (("", 1, ""),)

