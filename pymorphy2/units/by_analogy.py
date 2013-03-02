# -*- coding: utf-8 -*-
"""
Analogy analyzer units
----------------------

This module provides analyzer units that analyzes unknown words by looking
at how similar known words are analyzed.

"""

from __future__ import absolute_import, unicode_literals, division

import operator

from pymorphy2.units.base import BaseAnalyzerUnit
from pymorphy2.units.utils import add_parse_if_not_seen, add_tag_if_not_seen
from pymorphy2.utils import word_splits


class KnownPrefixAnalyzer(BaseAnalyzerUnit):
    """
    Parse the word by checking if it starts with a known prefix
    and parsing the reminder.

    Example: псевдокошка -> (псевдо) + кошка.
    """

    terminal = True
    ESTIMATE_DECAY = 0.75
    MIN_REMINDER_LENGTH = 3

    def _word_prefixes(self, word):
        return sorted(
            self.dict.prediction_prefixes.prefixes(word),
            key=len,
            reverse=True,
        )

    def parse(self, word, seen_parses):
        result = []
        for prefix in self._word_prefixes(word):
            unprefixed_word = word[len(prefix):]

            if len(unprefixed_word) < self.MIN_REMINDER_LENGTH:
                continue

            method = (self, prefix)

            for fixed_word, tag, normal_form, para_id, idx, estimate, methods in self.morph.parse(unprefixed_word):

                if not tag.is_productive():
                    continue

                parse = (
                    prefix+fixed_word, tag, prefix+normal_form,
                    para_id, idx, estimate*self.ESTIMATE_DECAY,
                    methods+(method,)
                )

                add_parse_if_not_seen(parse, result, seen_parses)

        return result

    def tag(self, word, seen_tags):
        result = []
        for prefix in self._word_prefixes(word):
            unprefixed_word = word[len(prefix):]

            if len(unprefixed_word) < self.MIN_REMINDER_LENGTH:
                continue

            for tag in self.morph.tag(unprefixed_word):
                if not tag.is_productive():
                    continue
                add_tag_if_not_seen(tag, result, seen_tags)

        return result


class UnknownPrefixAnalyzer(BaseAnalyzerUnit):
    """
    Parse the word by parsing only the word suffix
    (with restrictions on prefix & suffix lengths).

    Example: байткод -> (байт) + код

    """
    terminal = False
    ESTIMATE_DECAY = 0.5

    def parse(self, word, seen_parses):
        result = []
        for prefix, unprefixed_word in word_splits(word):

            method = (self, prefix)

            for fixed_word, tag, normal_form, para_id, idx, estimate, methods in self.dict.parse(unprefixed_word):

                if not tag.is_productive():
                    continue

                parse = (prefix+fixed_word, tag, prefix+normal_form,
                         para_id, idx, estimate*self.ESTIMATE_DECAY,
                         methods+(method,))
                add_parse_if_not_seen(parse, result, seen_parses)

        return result

    def tag(self, word, seen_tags):
        result = []
        for _, unprefixed_word in word_splits(word):
            for tag in self.dict.tag(unprefixed_word):

                if not tag.is_productive():
                    continue

                add_tag_if_not_seen(tag, result, seen_tags)

        return result


class KnownSuffixAnalyzer(BaseAnalyzerUnit):
    """
    Parse the word by checking how the words with similar suffixes
    are parsed.

    Example: бутявкать -> ...вкать

    """

    terminal = False
    ESTIMATE_DECAY = 0.5

    def __init__(self, morph):
        super(KnownSuffixAnalyzer, self).__init__(morph)

        self._paradigm_prefixes = list(reversed(list(enumerate(self.dict.paradigm_prefixes))))
        max_suffix_length = self.dict.meta['prediction_options']['max_suffix_length']
        self._prediction_splits = list(reversed(range(1, max_suffix_length+1)))


    def parse(self, word, seen_parses):
        result = []

        # smoothing; XXX: isn't max_cnt better?
        total_counts = [1] * len(self._paradigm_prefixes)

        for prefix_id, prefix in self._paradigm_prefixes:

            if not word.startswith(prefix):
                continue

            suffixes_dawg = self.dict.prediction_suffixes_dawgs[prefix_id]

            for i in self._prediction_splits:
                end = word[-i:]  # XXX: this should be counted once, not for each prefix
                para_data = suffixes_dawg.similar_items(end, self.dict.ee)

                for fixed_suffix, parses in para_data:
                    method = (self, fixed_suffix)

                    for cnt, para_id, idx in parses:
                        tag = self.dict.build_tag_info(para_id, idx)

                        if not tag.is_productive():
                            continue
                        total_counts[prefix_id] += cnt

                        fixed_word = word[:-i] + fixed_suffix
                        normal_form = self.dict.build_normal_form(para_id, idx, fixed_word)

                        parse = (cnt, fixed_word, tag, normal_form,
                                 para_id, idx, prefix_id, (method,))
                        reduced_parse = parse[1:4]
                        if reduced_parse in seen_parses:
                            continue

                        result.append(parse)

                if total_counts[prefix_id] > 1:
                    break

        result = [
            (fixed_word, tag, normal_form, para_id, idx, cnt/total_counts[prefix_id] * self.ESTIMATE_DECAY, methods)
            for (cnt, fixed_word, tag, normal_form, para_id, idx, prefix_id, methods) in result
        ]
        result.sort(key=operator.itemgetter(5), reverse=True)
        return result


    def tag(self, word, seen_tags):
        # XXX: the result order may be different from
        # ``self.parse(...)``.

        result = []

        for prefix_id, prefix in self._paradigm_prefixes:

            if not word.startswith(prefix):
                continue

            suffixes_dawg = self.dict.prediction_suffixes_dawgs[prefix_id]

            for i in self._prediction_splits:
                end = word[-i:]  # XXX: this should be counted once, not for each prefix
                para_data = suffixes_dawg.similar_items(end, self.dict.ee)
                found = False

                for fixed_suffix, parses in para_data:
                    for cnt, para_id, idx in parses:

                        tag = self.dict.build_tag_info(para_id, idx)

                        if not tag.is_productive():
                            continue

                        found = True
                        if tag in seen_tags:
                            continue
                        seen_tags.add(tag)
                        result.append((cnt, tag))

                if found:
                    break

        result.sort(reverse=True)
        return [tag for cnt, tag in result]



