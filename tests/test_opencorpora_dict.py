# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from pymorphy2 import opencorpora_dict

class TestToParadigm(object):

    def test_simple(self):
        lemma = [
            [
              "ЯРЧЕ",
              "COMP,Qual"
            ],
            [
              "ЯРЧЕЙ",
              "COMP,Qual V-ej"
            ],
        ]
        stem, forms = opencorpora_dict._to_paradigm(lemma)
        assert stem == "ЯРЧЕ"
        assert forms == (
            ("", "COMP,Qual", ""),
            ("Й", "COMP,Qual V-ej", ""),
        )

    def test_single_prefix(self):
        lemma = [
            [
              "ЯРЧЕ",
              "COMP,Qual"
            ],
            [
              "ПОЯРЧЕ",
              "COMP,Qual Cmp2"
            ],
        ]
        stem, forms = opencorpora_dict._to_paradigm(lemma)
        assert stem == "ЯРЧЕ"
        assert forms == (
            ("", "COMP,Qual", ""),
            ("", "COMP,Qual Cmp2", "ПО"),
        )


    def test_multiple_prefixes(self):
        lemma = [
            [
              "ЯРЧЕ",
              "COMP,Qual"
            ],
            [
              "ЯРЧЕЙ",
              "COMP,Qual V-ej"
            ],
            [
              "ПОЯРЧЕ",
              "COMP,Qual Cmp2"
            ],
            [
              "ПОЯРЧЕЙ",
              "COMP,Qual Cmp2,V-ej"
            ],
            [
              "НАИЯРЧАЙШИЙ",
              "ADJF,Supr,Qual masc,sing,nomn"
            ],
        ]
        stem, forms = opencorpora_dict._to_paradigm(lemma)
        print(stem, forms)
        assert stem == 'ЯРЧ'

    def test_multiple_prefixes_2(self):
        lemma = [
            ["ПОДРОБНЕЙШИЙ", 1],
            ["НАИПОДРОБНЕЙШИЙ", 2],
            ["ПОПОДРОБНЕЕ", 3]
        ]
        stem, forms = opencorpora_dict._to_paradigm(lemma)
        print(stem, forms)
        assert stem == 'ПОДРОБНЕ'
        assert forms == (
            ("ЙШИЙ", 1, ""),
            ("ЙШИЙ", 2, "НАИ"),
            ("Е", 3, "ПО"),
        )

