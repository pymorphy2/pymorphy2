# -*- coding: utf-8 -*-
"""
Analyzer units for abbreviated words
------------------------------------
"""
from __future__ import absolute_import, unicode_literals, division
from pymorphy2.units.base import BaseAnalyzerUnit


class _InitialsAnalyzer(BaseAnalyzerUnit):
    SCORE = 0.1
    LETTERS = set('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ')
    TAG_PATTERN = None

    def __init__(self, morph):
        if self.TAG_PATTERN is None:
            raise ValueError("Define TAG_PATTERN in a subclass")

        super(_InitialsAnalyzer, self).__init__(morph)

        if 'Init' not in self.morph.TagClass.KNOWN_GRAMMEMES:
            self.morph.TagClass.add_grammemes_to_known('Init', 'иниц')

        self._tags = self._get_gender_case_tags(self.TAG_PATTERN)

    def _get_gender_case_tags(self, pattern):
        return [
            self.morph.TagClass(pattern % {'gender': gender, 'case': case})
            for gender in ['masc', 'femn']
            for case in ['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct']
        ]

    def parse(self, word, word_lower, seen_parses):
        if word not in self.LETTERS:
            return []
        return [
            (word_lower, tag, word_lower, self.SCORE, ((self, word),))
            for tag in self._tags
        ]

    def tag(self, word, word_lower, seen_tags):
        if word not in self.LETTERS:
            return []
        return self._tags[:]


class AbbreviatedFirstNameAnalyzer(_InitialsAnalyzer):
    TAG_PATTERN = 'NOUN,anim,%(gender)s,Sgtm,Name,Fixd,Abbr,Init sing,%(case)s'

    def __init__(self, morph):
        super(AbbreviatedFirstNameAnalyzer, self).__init__(morph)
        self._tags_masc = [tag for tag in self._tags if 'masc' in tag]
        self._tags_femn = [tag for tag in self._tags if 'femn' in tag]
        assert self._tags_masc + self._tags_femn == self._tags

    def get_lexeme(self, form):
        # 2 lexemes: masc and femn
        fixed_word, form_tag, normal_form, score, methods_stack = form
        tags = self._tags_masc if 'masc' in form_tag else self._tags_femn
        return [
            (fixed_word, tag, normal_form, score, methods_stack)
            for tag in tags
        ]

    def normalized(self, form):
        # don't normalize female names to male names
        fixed_word, form_tag, normal_form, score, methods_stack = form
        tags = self._tags_masc if 'masc' in form_tag else self._tags_femn
        return fixed_word, tags[0], normal_form, score, methods_stack


class AbbreviatedPatronymicAnalyzer(_InitialsAnalyzer):
    TAG_PATTERN = 'NOUN,anim,%(gender)s,Sgtm,Patr,Fixd,Abbr,Init sing,%(case)s'

    def get_lexeme(self, form):
        fixed_word, _, normal_form, score, methods_stack = form
        return [
            (fixed_word, tag, normal_form, score, methods_stack)
            for tag in self._tags
        ]

    def normalized(self, form):
        fixed_word, _, normal_form, score, methods_stack = form
        return fixed_word, self._tags[0], normal_form, score, methods_stack
