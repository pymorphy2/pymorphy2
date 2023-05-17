# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import inspect

from pymorphy2.utils import kwargs_repr
from pymorphy2.units.utils import (
    without_last_method,
    append_method,
    add_tag_if_not_seen,
)


class BaseAnalyzerUnit(object):
    """
    Base class for analyzer units.

    For parsing to work subclasses must implement `parse` method;
    as an optimization they may also override `tag` method.

    For inflection to work (this includes normalization) a subclass
    must implement `normalized` and `get_lexeme` methods.

    In __init__ method all parameters must be saved as instance variables
    for analyzer unit to work.
    """
    morph = None
    dict = None
    _repr_skip_value_params = None

    def init(self, morph):
        self.morph = morph
        self.dict = morph.dictionary

    def clone(self):
        return self.__class__(**self._get_params())

    def parse(self, word, word_lower, seen_parses):
        raise NotImplementedError()

    def tag(self, word, word_lower, seen_tags):
        # By default .tag() uses .parse().
        # Usually it is possible to write a more efficient implementation;
        # analyzers should do it when possible.
        result = []
        for p in self.parse(word, word_lower, set()):
            add_tag_if_not_seen(p[1], result, seen_tags)
        return result

    def normalized(self, form):
        raise NotImplementedError()

    def get_lexeme(self, form):
        raise NotImplementedError()

    def __repr__(self):
        cls_text = self.__class__.__name__
        kwargs_text = kwargs_repr(self._get_params(),
                                  self._repr_skip_value_params)
        return str("%s(%s)") % (cls_text, kwargs_text)

    @classmethod
    def _get_param_names(cls):
        """
        Get parameter names for the analyzer unit.
        It works by introspecting `__init__` arguments.
        `__init__` method must not use *args.
        """
        if cls.__init__ is object.__init__:
            return []
        args, *_ = inspect.getfullargspec(cls.__init__)
        return sorted(args[1:])

    def _get_params(self):
        """ Return a dict with the parameters for this analyzer unit. """
        return dict(
            (key, getattr(self, key, None)) for key in self._get_param_names()
        )



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
