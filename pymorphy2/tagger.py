# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import os
import collections
from pymorphy2 import opencorpora_dict
from pymorphy2.constants import LEMMA_PREFIXES

def _split_word(word, min_reminder=3, max_prefix_length=5):
    max_split = min(max_prefix_length, len(word)-min_reminder)
    split_indexes = range(1, 1+max_split)
    return [(word[:i], word[i:]) for i in split_indexes]

class Morph(object):

    env_variable = 'PYMORPHY2_DICT_PATH'

    def __init__(self, dct):
        self._dictionary = dct
        self._ee = dct.words.compile_replaces({'Е': 'Ё'})

    @classmethod
    def load(cls, path=None):
        """
        Creates a Morph object using dictionaries at ``path``.

        If ``path`` is None then the path is obtained from
        ``PYMORPHY2_DICT_PATH`` enviroment variable.
        """
        if path is None:
            if cls.env_variable not in os.environ:
                raise ValueError("Please pass a path to dictionaries or set %s environment variable" % cls.env_variable)
            path = os.environ[cls.env_variable]

        dct = opencorpora_dict.load(path)
        return cls(dct)

    def parse(self, word):
        """
        Returns a list of (fixed_word, tag, normal_form) tuples.
        """
        res = self._parse_as_known(word)
        if not res:
            res = self._parse_as_word_with_known_prefix(word)
        if not res:
            res = self._parse_as_word_with_unknown_prefix(word)
        if not res:
            res = self._parse_as_word_with_known_suffix(word)
        return res

    def _parse_as_known(self, word):
        res = []
        para_normal_forms = {}

        para_data = self._dictionary.words.similar_items(word, self._ee)

        for fixed_word, parse in para_data: # fixed_word is a word with proper Ё letters
            for para_id, idx in parse:

                if para_id not in para_normal_forms:
                    normal_form = self._build_normal_form(para_id, idx, fixed_word)
                    para_normal_forms[para_id] = normal_form
                else:
                    normal_form = para_normal_forms[para_id]

                tag = self._build_tag_info(para_id, idx)

                res.append(
                    (fixed_word, tag, normal_form)
                )

        return res

    def _parse_as_word_with_known_prefix(self, word):
        res = []
        word_prefixes = self._dictionary.prediction_prefixes.prefixes(word)
        for prefix in word_prefixes:
            unprefixed_word = word[len(prefix):]
            parses = self.parse(unprefixed_word)
            res.extend([
                (prefix+fixed_word, tag, prefix+normal_form)
                for (fixed_word, tag, normal_form) in parses
            ])
        return res

    def _parse_as_word_with_unknown_prefix(self, word):
        res = []
        for prefix, truncated_word in _split_word(word):
            parses = self._parse_as_known(truncated_word)
            res.extend([
                (prefix+fixed_word, tag, prefix+normal_form)
                for (fixed_word, tag, normal_form) in parses
            ])

        return res

    def _parse_as_word_with_known_suffix(self, word):
        result = []
        for i in 5,4,3,2,1:
            end = word[-i:]
            para_data = self._dictionary.prediction_suffixes.similar_items(end, self._ee)

            for fixed_suffix, parse in para_data:
                for cnt, para_id, idx in reversed(parse):
                    fixed_word = word[:-i] + fixed_suffix
                    normal_form = self._build_normal_form(para_id, idx, fixed_word)
                    tag = self._build_tag_info(para_id, idx)
                    result.append(
                        (cnt, fixed_word, tag, normal_form)
                    )

            if result:
                result = [tpl[1:] for tpl in sorted(result, reverse=True)] # remove counts
                break

        return result

    def normal_forms(self, word):
        seen = set()
        result = []
        for fixed_word, tag, normal_form in self.parse(word):
            if normal_form not in seen:
                result.append(normal_form)
                seen.add(normal_form)
        return result

    # ====== tag ========

    def tag(self, word):
        res = self._tag_as_known(word)
        if not res:
            res = self._tag_as_word_with_known_prefix(word)
        if not res:
            res = self._tag_as_word_with_unknown_prefix(word)
        if not res:
            res = self._tag_using_suffix(word)
        return res

    def _tag_as_known(self, word):
        para_data = self._dictionary.words.similar_item_values(word, self._ee)

        # avoid extra attribute lookups
        paradigms = self._dictionary.paradigms
        gramtab = self._dictionary.gramtab

        # tag known word
        result = []
        for parse in para_data:
            for para_id, idx in parse:
                # result.append(self._build_tag_info(para_id, idx))
                # .tag_info is unrolled for speed
                paradigm = paradigms[para_id]
                paradigm_len = len(paradigm) // 3
                tag_id = paradigm[paradigm_len + idx]
                result.append(gramtab[tag_id])

        return result

    def _tag_as_word_with_known_prefix(self, word):
        res = []
        word_prefixes = self._dictionary.prediction_prefixes.prefixes(word)
        for pref in word_prefixes:
            unprefixed_word = word[len(pref):]
            res.extend(self.tag(unprefixed_word))
        return res

    def _tag_as_word_with_unknown_prefix(self, word):
        res = []
        for _, truncated_word in _split_word(word):
            res.extend(self._tag_as_known(truncated_word))
            # XXX: remove non-productive classes?

        return res

    def _tag_using_suffix(self, word):
        result = []
        for i in 5,4,3,2,1:
            end = word[-i:]
            para_data = self._dictionary.prediction_suffixes.similar_item_values(end, self._ee)

            for parse in para_data:
                for cnt, para_id, idx in parse:
                    result.append(
                        (cnt, self._build_tag_info(para_id, idx))
                    )

            if result:
                result = [tpl[1] for tpl in sorted(result, reverse=True)] # remove counts
                break

        return result

    # ==== dictionary access utilities ===

    def _build_tag_info(self, para_id, idx):
        paradigm = self._dictionary.paradigms[para_id]
        tag_id = paradigm[len(paradigm) // 3 + idx]
        return self._dictionary.gramtab[tag_id]

    def _build_paradigm_info(self, para_id):
        paradigm = self._dictionary.paradigms[para_id]
        paradigm_len = len(paradigm) // 3
        res = []
        for idx in range(paradigm_len):
            prefix_id = paradigm[paradigm_len*2 + idx]
            prefix = LEMMA_PREFIXES[prefix_id]

            suffix_id = paradigm[idx]
            suffix = self._dictionary.suffixes[suffix_id]

            res.append(
                (prefix, self._build_tag_info(para_id, idx), suffix)
            )
        return res

    def _build_normal_form(self, para_id, idx, fixed_word):

        if idx == 0: # a shortcut: normal form is a word itself
            return fixed_word

        paradigms = self._dictionary.paradigms
        suffixes = self._dictionary.suffixes

        paradigm = paradigms[para_id]
        paradigm_len = len(paradigm) // 3

        prefix_id = paradigm[paradigm_len*2 + idx]
        prefix = LEMMA_PREFIXES[prefix_id]

        suffix_id = paradigm[idx]
        suffix = suffixes[suffix_id]

        if len(suffix):
            stem = fixed_word[len(prefix):-len(suffix)]
        else:
            stem = fixed_word[len(prefix):]

        normal_prefix_id = paradigm[paradigm_len*2 + 0]
        normal_suffix_id = paradigm[0]

        normal_prefix = LEMMA_PREFIXES[normal_prefix_id]
        normal_suffix = suffixes[normal_suffix_id]

        return normal_prefix + stem + normal_suffix


    # ====== misc =========

    def meta(self):
        return self._dictionary.meta

