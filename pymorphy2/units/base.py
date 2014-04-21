# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from pymorphy2.units.utils import without_last_method, append_method


class BaseAnalyzerUnit(object):

    def __init__(self, morph):
        """
        :type morph: pymorphy2.analyzer.MorphAnalyzer
        :type self.dict: pymorphy2.analyzer.Dictionary
        """
        self.morph = morph
        self.dict = morph.dictionary

    def parse(self, word, word_lower, seen_parses):
        raise NotImplementedError()

    def tag(self, word, word_lower, seen_tags):
        raise NotImplementedError()

    def __repr__(self):
        return str("<%s>") % self.__class__.__name__


class AnalogyAnalizerUnit(BaseAnalyzerUnit):

    def normalized(self, form):
        base_analyzer, this_method = self._method_info(form)
        return self._normalized(form, base_analyzer, this_method)

    def _normalized(self, form, base_analyzer, this_method):
        normalizer = self.normalizer(form, this_method)

        form = without_last_method(next(normalizer))
        normal_form = normalizer.send(base_analyzer.normalized(form))
        return append_method(normal_form, this_method)

    def get_lexeme(self, form):
        base_analyzer, this_method = self._method_info(form)
        return self._get_lexeme(form, base_analyzer, this_method)

    def _get_lexeme(self, form, base_analyzer, this_method):
        lexemizer = self.lexemizer(form, this_method)
        form = without_last_method(next(lexemizer))
        lexeme = lexemizer.send(base_analyzer.get_lexeme(form))
        return [append_method(f, this_method) for f in lexeme]

    def normalizer(self, form, this_method):
        """ A coroutine for normalization """

        # 1. undecorate form:
        # form = undecorate(form)

        # 2. get normalized version of undecorated form:
        normal_form = yield form

        # 3. decorate the normalized version:
        # normal_form = decorate(normal_form)

        # 4. return the result
        yield normal_form

    def lexemizer(self, form, this_method):
        """ A coroutine for preparing lexemes """
        lexeme = yield form
        yield lexeme

    def _method_info(self, form):
        methods_stack = form[4]
        base_method, this_method = methods_stack[-2:]
        base_analyzer = base_method[0]
        return base_analyzer, this_method
