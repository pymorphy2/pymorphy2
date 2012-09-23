# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import os
from pymorphy2 import opencorpora_dict
from pymorphy2.constants import LEMMA_PREFIXES, PREDICTION_PREFIXES

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

    def tag(self, word):
        res = self._tag_as_known(word)
        if not res:
            res = self._tag_as_prefixed(word)
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
                paradigm = paradigms[para_id]
                paradigm_len = len(paradigm) // 3
                tag_id = paradigm[paradigm_len + idx]
                result.append(gramtab[tag_id])

        return result

    def _tag_as_prefixed(self, word):
        word_prefixes = self._dictionary.prediction_prefixes.prefixes(word)
        res = []
        for pref in word_prefixes:
            unprefixed_word = word[len(pref):]
            res.extend(self.tag(unprefixed_word))
        return res

    def normal_forms(self, word):
        res = self._known_normal_forms(word)
        if not res:
            res = self._prefixed_normal_forms(word)
        return res

    def _prefixed_normal_forms(self, word):
        word_prefixes = self._dictionary.prediction_prefixes.prefixes(word)
        res = []
        for pref in word_prefixes:
            unprefixed_word = word[len(pref):]
            res.extend([pref+w for w in self.normal_forms(unprefixed_word)])
        return res

    def _known_normal_forms(self, word):
        para_data = self._dictionary.words.similar_items(word, self._ee)

        # avoid extra attribute lookups
        paradigms = self._dictionary.paradigms
        suffixes = self._dictionary.suffixes

        result = []
        seen_paradigms = set()
        seen_forms = set()

        for fixed_word, parse in para_data: # fixed_word is a word with proper Ё letters
            for para_id, idx in parse:

                if para_id in seen_paradigms:
                    continue
                seen_paradigms.add(para_id)

                # a shortcut: normal form is a word itself
                if idx == 0:
                    if fixed_word not in seen_forms:
                        seen_forms.add(fixed_word)
                        result.append(fixed_word)
                    continue

                # get the normal form
                paradigm = paradigms[para_id]
                paradigm_len = len(paradigm) // 3

                prefix_id = paradigm[paradigm_len*2 + idx]
                prefix = LEMMA_PREFIXES[prefix_id]

                suffix_id = paradigm[idx]
                suffix = suffixes[suffix_id]

                stem = fixed_word[len(prefix):-len(suffix)]

                normal_prefix_id = paradigm[paradigm_len*2 + 0]
                normal_suffix_id = paradigm[0]

                normal_prefix = LEMMA_PREFIXES[normal_prefix_id]
                normal_suffix = suffixes[normal_suffix_id]

                normal_form = normal_prefix + stem + normal_suffix

                if normal_form not in seen_forms:
                    seen_forms.add(normal_form)
                    result.append(normal_form)
        return result

    def meta(self):
        return self._dictionary.meta