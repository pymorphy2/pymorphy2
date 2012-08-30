# cython: profile=True
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import os
from . import data


class Morph(object):

    env_variable = 'PYMORPHY2_DICT_PATH'

    def __init__(self, dct):
        self._dictionary = dct

    @classmethod
    def load(cls, path=None, use_mmap=False):
        """
        Creates a Morph object using dictionaries at ``path``.

        If ``path`` is None then the path is obtained from
        ``PYMORPHY2_DICT_PATH`` enviroment variable.
        """
        if path is None:
            if cls.env_variable not in os.environ:
                raise ValueError("Please pass a path to dictionaries or set %s environment variable" % cls.env_variable)
            path = os.environ[cls.env_variable]

        dct = data.load_dict(path, use_mmap=use_mmap)
        return cls(dct)

    def tag(self, word):
        para_data = self._dictionary.words.get(word, [])

        # avoid extra attribute lookups
        paradigms = self._dictionary.paradigms
        gramtab = self._dictionary.gramtab

        # tag known word
        result = []
        for para_id, idx in para_data:
            tag_id = paradigms[para_id][idx][1]
            result.append(gramtab[tag_id])

        return result


    def normal_forms(self, word):
        para_data = self._dictionary.words.get(word, [])

        # avoid extra attribute lookups
        paradigms = self._dictionary.paradigms

        result = []
        seen = set()
        for para_id, idx in para_data:

            if para_id in seen:
                continue
            seen.add(para_id)

            if idx == 0:
                result.append(word)
                continue

            form = paradigms[para_id][idx]
            stem = word[len(form[2]):-len(form[0])]

            normal_form = paradigms[para_id][0]
            result.append(normal_form[2] + stem + normal_form[0])
        return result
