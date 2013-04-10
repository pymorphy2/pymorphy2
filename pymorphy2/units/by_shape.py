# -*- coding: utf-8 -*-
"""
Analyzer units that analyzes non-word tokes
-------------------------------------------
"""

from __future__ import absolute_import, unicode_literals, division

from pymorphy2.units.base import BaseAnalyzerUnit
from pymorphy2.shapes import is_latin, is_punctuation, is_roman_number

class _ShapeAnalyzer(BaseAnalyzerUnit):

    terminal = True
    ESTIMATE = 0.9
    EXTRA_GRAMMEMES = []

    def __init__(self, morph):
        super(_ShapeAnalyzer, self).__init__(morph)
        self.morph.TagClass.KNOWN_GRAMMEMES.update(self.EXTRA_GRAMMEMES)

    def parse(self, word, word_lower, seen_parses):
        shape = self.check_shape(word, word_lower)
        if not shape:
            return []

        methods = ((self, word),)
        return [(word_lower, self.get_tag(word, shape), word_lower, self.ESTIMATE, methods)]

    def tag(self, word, word_lower, seen_tags):
        shape = self.check_shape(word, word_lower)
        if not shape:
            return []
        return [self.get_tag(word, shape)]

    def get_lexeme(self, form):
        return [form]

    def normalized(self, form):
        return form

    # implement these 2 methods in a subclass:
    def check_shape(self, word, word_lower):
        raise NotImplementedError()

    def get_tag(self, word, shape):
        raise NotImplementedError()


class _SingleShapeAnalyzer(_ShapeAnalyzer):
    TAG_STR = None

    def __init__(self, morph):
        assert self.TAG_STR is not None
        self.EXTRA_GRAMMEMES = self.TAG_STR.split(',')
        super(_SingleShapeAnalyzer, self).__init__(morph)
        self._tag = self.morph.TagClass(self.TAG_STR)

    def get_tag(self, word, shape):
        return self._tag


class PunctuationAnalyzer(_SingleShapeAnalyzer):
    """
    This analyzer tags punctuation marks as "PNCT".
    Example: "," -> PNCT
    """
    TAG_STR = 'PNCT'

    def check_shape(self, word, word_lower):
        return is_punctuation(word)


class LatinAnalyzer(_SingleShapeAnalyzer):
    """
    This analyzer marks latin words with "LATN" tag.
    Example: "pdf" -> LATN
    """
    TAG_STR = 'LATN'

    def check_shape(self, word, word_lower):
        return is_latin(word)


class NumberAnalyzer(_SingleShapeAnalyzer):
    """
    This analyzer marks numbers with "NUMB" tag.
    Example: "12" -> NUMB

    .. note::

        Don't confuse it with "NUMR": "тридцать" -> NUMR

    """
    TAG_STR = 'NUMB'

    def check_shape(self, word, word_lower):
        return word.isdigit()


class RomanNumberAnalyzer(_SingleShapeAnalyzer):
    TAG_STR = 'ROMN'
    terminal = False  # give LatinAnalyzer a chance

    def check_shape(self, word, word_lower):
        return is_roman_number(word)
