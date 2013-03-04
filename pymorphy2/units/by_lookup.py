# -*- coding: utf-8 -*-
"""
Dictionary analyzer unit
------------------------
"""
from __future__ import absolute_import, division, unicode_literals
import logging
from pymorphy2.units.base import BaseAnalyzerUnit


logger = logging.getLogger(__name__)



class DictionaryAnalyzer(BaseAnalyzerUnit):
    """
    Analyzer unit that analyzes word using dictionary.
    """

    terminal = True

    def parse(self, word, seen_parses):
        """
        Parse a word using this dictionary.
        """
        res = []
        para_normal_forms = {}
        para_data = self.dict.words.similar_items(word, self.dict.ee)

        for fixed_word, parses in para_data:
            # `fixed_word` is a word with proper ё letters

            method = ((self, fixed_word),)

            for para_id, idx in parses:

                if para_id not in para_normal_forms:
                    normal_form = self.dict.build_normal_form(para_id, idx, fixed_word)
                    para_normal_forms[para_id] = normal_form
                else:
                    normal_form = para_normal_forms[para_id]

                tag = self.dict.build_tag_info(para_id, idx)

                parse = (fixed_word, tag, normal_form,
                         para_id, idx, 1.0, method)

                res.append(parse)

        return res

    def tag(self, word, seen_tags):
        """
        Tag a word using this dictionary.
        """
        para_data = self.dict.words.similar_item_values(word, self.dict.ee)

        # avoid extra attribute lookups
        paradigms = self.dict.paradigms
        gramtab = self.dict.gramtab

        # tag known word
        result = []
        for parse in para_data:
            for para_id, idx in parse:
                # result.append(self.build_tag_info(para_id, idx))
                # .build_tag_info is unrolled for speed
                paradigm = paradigms[para_id]
                paradigm_len = len(paradigm) // 3
                tag_id = paradigm[paradigm_len + idx]
                result.append(gramtab[tag_id])

        return result

    def get_lexeme(self, form, methods_stack):
        """
        Return a lexeme (given a parsed word).
        """
        assert len(methods_stack) == 0 or methods_stack[0][0] is self

        fixed_word, tag, normal_form, para_id, idx, estimate, _methods_stack = form
        stem = self.dict.build_stem(
            self.dict.paradigms[para_id], idx, fixed_word
        )

        result = []
        paradigm = self.dict.build_paradigm_info(para_id)
        for index, (_prefix, _tag, _suffix) in enumerate(paradigm):
            word = _prefix + stem + _suffix

            result.append(
                (word, _tag, normal_form, para_id, index, estimate, _methods_stack)
            )

        return result

    def normalized(self, form):
        fixed_word, tag, normal_form, para_id, idx, estimate, methods_stack = form

        if idx == 0:
            return form

        tag = self.dict.build_tag_info(para_id, 0)
        return (normal_form, tag, normal_form,
                para_id, 0, estimate, methods_stack)


    def __repr__(self):
        return str("<%s>") % self.__class__.__name__
