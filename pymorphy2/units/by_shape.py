# -*- coding: utf-8 -*-
"""
Analyzer units that analyzes non-word tokes
-------------------------------------------
"""

from __future__ import absolute_import, unicode_literals, division

from pymorphy2.units.base import BaseAnalyzerUnit
from pymorphy2.shapes import is_latin, is_punctuation

class _ShapeAnalyzer(BaseAnalyzerUnit):
    ESTIMATE = 0.5
    EXTRA_GRAMMEMES = []

    def __init__(self, morph):
        super(_ShapeAnalyzer, self).__init__(morph)
        self.morph.TagClass.KNOWN_GRAMMEMES.update(self.EXTRA_GRAMMEMES)

    def parse(self, word, seen_parses):
        shape = self._check_shape(word)
        if not shape:
            return []

        return [(
            word, self._get_tag(word, shape), word,
            None, None, self.ESTIMATE,
            ((self, ),),
        )]

    def tag(self, word, seen_tags):
        shape = self._check_shape(word)
        if not shape:
            return []
        return [self._get_tag(word, shape)]

    def get_lexeme(self, form, methods_stack):
        return [form]

    def normalized(self, form):
        return form

    # implement these 2 methods in a subclass:
    def _check_shape(self, word):
        raise NotImplementedError()

    def _get_tag(self, word, shape):
        raise NotImplementedError()



class PunctuationAnalyzer(_ShapeAnalyzer):
    """
    This analyzer tags punctuation marks as "PNCT".
    Example: "," -> PNCT
    """
    terminal = True
    ESTIMATE = 0.9
    EXTRA_GRAMMEMES = ['PNCT']

    def __init__(self, morph):
        super(PunctuationAnalyzer, self).__init__(morph)
        self._tag = self.morph.TagClass('PNCT')

    def _get_tag(self, word, shape):
        return self._tag

    def _check_shape(self, word):
        return is_punctuation(word)


class LatinAnalyzer(_ShapeAnalyzer):
    """
    This analyzer marks latin words with "LATN" tag.
    Example: "pdf" -> LATN
    """
    terminal = True
    ESTIMATE = 0.9
    EXTRA_GRAMMEMES = ['LATN']

    def __init__(self, morph):
        super(LatinAnalyzer, self).__init__(morph)
        self._tag = self.morph.TagClass('LATN')

    def _get_tag(self, word, shape):
        return self._tag

    def _check_shape(self, word):
        return is_latin(word)


