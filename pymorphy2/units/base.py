# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division

class BaseAnalyzerUnit(object):

    terminal = False

    def __init__(self, morph):
        """
        :type morph: pymorphy2.analyzer.MorphAnalyzer
        :type self.dict: pymorphy2.analyzer.Dictionary
        """
        self.morph = morph
        self.dict = morph.dictionary


    def parse(self, word, seen_parses):
        raise NotImplementedError()

    def tag(self, word, seen_tags):
        raise NotImplementedError()


    def get_lexeme(self, form, methods_stack):
        # be default, analyzer gets a lexeme from a previous analyzer:
        last_method = methods_stack[-1]
        assert last_method[0] is self

        # if len(methods_stack) == 1:
        #     return self.dict.get_lexeme(form, [])

        assert len(methods_stack) > 1, len(methods_stack)
        previous_predictor = methods_stack[-2][0]
        return previous_predictor.get_lexeme(form, methods_stack[:-1])

    def normalized(self, form):
        raise NotImplementedError(form)

    def __repr__(self):
        return str("<%s>") % self.__class__.__name__

