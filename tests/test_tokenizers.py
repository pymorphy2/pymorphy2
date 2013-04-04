# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pymorphy2.tokenizers import word_tokenize

class TestSplit:

    def test_split_simple(self):
        assert word_tokenize('Мама мыла раму') == ['Мама', 'мыла', 'раму']
        assert word_tokenize('Постой, паровоз!') == ['Постой', ',', 'паровоз', '!']

    def test_split_hyphen(self):
        assert word_tokenize('Ростов-на-Дону') == ['Ростов-на-Дону']
        assert word_tokenize('Ура - победа') == ['Ура', '-', 'победа']

    def test_split_signs(self):
        assert word_tokenize('a+b=c_1') == ['a','+','b','=','c_1']

    def test_exctract_words(self):
        text = '''Это  отразилось: на количественном,и на качествен_ном
                - росте карельско-финляндского сотрудничества - офигеть! кони+лошади=масло.
                -сказал кто-то --нет--'''

        assert word_tokenize(text) == [
            'Это', 'отразилось', ':', 'на', 'количественном', ',', 'и', 'на',
            'качествен_ном', '-', 'росте', 'карельско-финляндского',
            'сотрудничества', '-', 'офигеть', '!', 'кони', '+', 'лошади',
            '=', 'масло', '.', '-сказал', 'кто-то', '--нет--',
        ]
