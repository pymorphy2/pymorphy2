# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division

class BaseAnalyzerUnit(object):

    terminal = False

    def __init__(self, morph):
        """
        @type morph: pymorphy2.analyzer.MorphAnalyzer
        @type self.dict: pymorphy2.analyzer.Dictionary
        """
        self.morph = morph
        self.dict = morph.dictionary

    def parse(self, word, seen_parses):
        raise NotImplementedError()

    def tag(self, word, seen_tags):
        raise NotImplementedError()

    def get_lexeme(self, form, methods):
        # be default, predictor gets a lexeme from a previous predictor:
        assert methods[-1][0] is self
        if len(methods) == 1:
            return self.dict.get_lexeme(form, [])

        assert len(methods) > 1, len(methods)
        previous_predictor = methods[-2][0]
        return previous_predictor.get_lexeme(form, methods[:-1])

    def normalized(self, form):
        return self.dict.normalized(form)

    def __repr__(self):
        return str("<%s>") % self.__class__.__name__

