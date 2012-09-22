# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import os
from . import data

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

        dct = data.load_dict(path)
        return cls(dct)

    def tag(self, word):
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
                tag_id = paradigm[idx + paradigm_len]
                result.append(gramtab[tag_id])

        return result

    def normal_forms(self, word):
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
                prefix = data.POSSIBLE_PREFIXES[prefix_id]

                suffix_id = paradigm[idx]
                suffix = suffixes[suffix_id]

                stem = fixed_word[len(prefix):-len(suffix)]

                normal_prefix_id = paradigm[paradigm_len*2 + 0]
                normal_suffix_id = paradigm[0]

                normal_prefix = data.POSSIBLE_PREFIXES[normal_prefix_id]
                normal_suffix = suffixes[normal_suffix_id]

                normal_form = normal_prefix + stem + normal_suffix

                if normal_form not in seen_forms:
                    seen_forms.add(normal_form)
                    result.append(normal_form)
        return result
