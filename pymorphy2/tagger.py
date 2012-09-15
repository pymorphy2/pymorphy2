# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
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
                tag_id = paradigms[para_id][idx][1]
                result.append(gramtab[tag_id])

        return result

    def normal_forms(self, word):
        para_data = self._dictionary.words.similar_items(word, self._ee)

        # avoid extra attribute lookups
        paradigms = self._dictionary.paradigms

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
                form = paradigms[para_id][idx]
                stem = fixed_word[len(form[2]):-len(form[0])]
                normal_form_data = paradigms[para_id][0]
                normal_form = normal_form_data[2] + stem + normal_form_data[0]

                if normal_form not in seen_forms:
                    seen_forms.add(normal_form)
                    result.append(normal_form)
        return result
