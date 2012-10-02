# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import os
import collections
from pymorphy2 import opencorpora_dict
from pymorphy2.constants import LEMMA_PREFIXES, NON_PRODUCTIVE_CLASSES
from pymorphy2.tagset import get_POS

#ParseResult = collections.namedtuple('ParseResult', 'fixed_word tag normal_form estimate')

class Morph(object):

    env_variable = 'PYMORPHY2_DICT_PATH'

    def __init__(self, dct):
        self._dictionary = dct
        self._ee = dct.words.compile_replaces({'Е': 'Ё'})
        self._non_productive_classes = NON_PRODUCTIVE_CLASSES[dct.meta['gramtab_format']]

    @classmethod
    def load(cls, path=None):
        """
        Creates a Morph object using dictionaries at ``path``.

        If ``path`` is None then the path is obtained from
        ``PYMORPHY2_DICT_PATH`` environment variable.
        """
        if path is None:
            if cls.env_variable not in os.environ:
                raise ValueError("Please pass a path to dictionaries or set %s environment variable" % cls.env_variable)
            path = os.environ[cls.env_variable]

        dct = opencorpora_dict.load(path)
        return cls(dct)

    def parse(self, word):
        """
        Returns a list of (fixed_word, tag, normal_form, _estimate) tuples.
        """
        res = self._parse_as_known(word)
        if not res:
            res = self._parse_as_word_with_known_prefix(word)
        if not res:
            seen = set()
            res = self._parse_as_word_with_unknown_prefix(word, seen)
            res.extend(self._parse_as_word_with_known_suffix(word, seen))
        return res

    def _parse_as_known(self, word):
        """
        Parses the word using a dictionary.
        """
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
                    (fixed_word, tag, normal_form, 1.0)
                )

        return res

    def _parse_as_word_with_known_prefix(self, word):
        """
        Parses the word by checking if it starts with a known prefix
        and parsing the reminder.
        """
        res = []
        ESTIMATE_DECAY = 0.75
        word_prefixes = self._dictionary.prediction_prefixes.prefixes(word)
        for prefix in word_prefixes:
            unprefixed_word = word[len(prefix):]

            for fixed_word, tag, normal_form, estimate in self.parse(unprefixed_word):
                if get_POS(tag) in self._non_productive_classes:
                    continue

                parse = (prefix+fixed_word, tag, prefix+normal_form, estimate*ESTIMATE_DECAY)
                res.append(parse)

        return res

    def _parse_as_word_with_unknown_prefix(self, word, _seen_parses=None):
        """
        Parses the word by parsing only the word suffix
        (with restrictions on prefix & suffix lengths).
        """
        if _seen_parses is None:
            _seen_parses = set()
        res = []
        ESTIMATE_DECAY = 0.5
        for prefix, unprefixed_word in _split_word(word):
            for fixed_word, tag, normal_form, estimate in self._parse_as_known(unprefixed_word):

                if get_POS(tag) in self._non_productive_classes:
                    continue

                parse = (prefix+fixed_word, tag, prefix+normal_form, estimate*ESTIMATE_DECAY)

                reduced_parse = parse[:3]
                if reduced_parse in _seen_parses:
                    continue
                _seen_parses.add(reduced_parse)

                res.append(parse)

        return res

    def _parse_as_word_with_known_suffix(self, word, _seen_parses=None):
        """
        Parses the word by checking how the words with similar suffixes
        are parsed.
        """
        if _seen_parses is None:
            _seen_parses = set()
        result = []
        ESTIMATE_DECAY = 0.5
        for i in 5,4,3,2,1:
            end = word[-i:]
            para_data = self._dictionary.prediction_suffixes.similar_items(end, self._ee)

            total_cnt = 1 # smoothing; XXX: isn't max_cnt better?
            for fixed_suffix, parse in para_data:
                for cnt, para_id, idx in reversed(parse):

                    tag = self._build_tag_info(para_id, idx)

                    if get_POS(tag) in self._non_productive_classes:
                        continue

                    total_cnt += cnt

                    fixed_word = word[:-i] + fixed_suffix
                    normal_form = self._build_normal_form(para_id, idx, fixed_word)

                    parse = (fixed_word, tag, normal_form, cnt)
                    reduced_parse = parse[:3]
                    if reduced_parse in _seen_parses:
                        continue

                    result.append(parse)

            if total_cnt > 1:
                result = [
                    (fixed_word, tag, normal_form, cnt/total_cnt * ESTIMATE_DECAY)
                    for (fixed_word, tag, normal_form, cnt) in sorted(result, reverse=True)
                ]
                break

        return result

    def normal_forms(self, word):
        """
        Returns a list of word normal forms.
        """
        seen = set()
        result = []
        for fixed_word, tag, normal_form, estimate in self.parse(word):
            if normal_form not in seen:
                result.append(normal_form)
                seen.add(normal_form)
        return result

    # ====== tag ========
    # XXX: one can use .parse method, but .tag is up to 2x faster.

    def tag(self, word):
        res = self._tag_as_known(word)
        if not res:
            res = self._tag_as_word_with_known_prefix(word)
        if not res:
            res = self._tag_as_word_with_unknown_prefix(word)
        if not res:
            res = self._tag_as_word_with_known_suffix(word)
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

    def _tag_as_word_with_known_suffix(self, word):
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
        """
        Returns gram. tag as a string.
        """
        paradigm = self._dictionary.paradigms[para_id]
        tag_info_offset = len(paradigm) // 3
        tag_id = paradigm[tag_info_offset + idx]
        return self._dictionary.gramtab[tag_id]

    def _build_paradigm_info(self, para_id):
        """
        Returns a list of

            (prefix, tag, suffix)

        tuples representing the paradigm.
        """
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
        """
        Builds a normal form.
        """

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


def _split_word(word, min_reminder=3, max_prefix_length=5):
    """
    Returns all splits of a word (taking in account min_reminder and
    max_prefix_length).
    """
    max_split = min(max_prefix_length, len(word)-min_reminder)
    split_indexes = range(1, 1+max_split)
    return [(word[:i], word[i:]) for i in split_indexes]
