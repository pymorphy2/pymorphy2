# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import operator

from .utils import word_splits

__all__ = [
    "KnownPrefixPredictor",
    "UnknownPrefixPredictor",
    "KnownSuffixPredictor",
]

class BasePredictor(object):
    terminal = NotImplemented

    def __init__(self, morph):
        self.morph = morph
        self.dict = morph.dictionary

    def parse(self, word, seen_parses=None):
        raise NotImplementedError()

    def tag(self, word, seen_tags=None):
        raise NotImplementedError()


class KnownPrefixPredictor(BasePredictor):
    """
    Parse the word by checking if it starts with a known prefix
    and parsing the reminder.
    """

    terminal = True
    ESTIMATE_DECAY = 0.75

    def parse(self, word, seen_parses=None):
        res = []
        word_prefixes = self.dict.prediction_prefixes.prefixes(word)
        for prefix in word_prefixes:
            unprefixed_word = word[len(prefix):]

            for fixed_word, tag, normal_form, para_id, idx, estimate in self.morph.parse(unprefixed_word):

                if not tag.is_productive():
                    continue

                parse = (prefix+fixed_word, tag, prefix+normal_form, para_id, idx, estimate*self.ESTIMATE_DECAY)
                res.append(parse)

        return res

    def tag(self, word, seen_tags=None):
        res = []
        word_prefixes = self.dict.prediction_prefixes.prefixes(word)
        for pref in word_prefixes:
            unprefixed_word = word[len(pref):]

            for tag in self.morph.tag(unprefixed_word):
                if not tag.is_productive():
                    continue
                res.append(tag)

        return res


class UnknownPrefixPredictor(BasePredictor):
    """
    Parse the word by parsing only the word suffix
    (with restrictions on prefix & suffix lengths).
    """
    terminal = False
    ESTIMATE_DECAY = 0.5

    def parse(self, word, seen_parses=None):
        if seen_parses is None:
            seen_parses = set()
        res = []
        for prefix, unprefixed_word in word_splits(word):
            for fixed_word, tag, normal_form, para_id, idx, estimate in self.dict.parse(unprefixed_word):

                if not tag.is_productive():
                    continue

                parse = (prefix+fixed_word, tag, prefix+normal_form, para_id, idx, estimate*self.ESTIMATE_DECAY)

                reduced_parse = parse[:3]
                if reduced_parse in seen_parses:
                    continue
                seen_parses.add(reduced_parse)

                res.append(parse)

        return res

    def tag(self, word, seen_tags=None):
        if seen_tags is None:
            seen_tags = set()

        res = []
        for _, unprefixed_word in word_splits(word):
            for tag in self.dict.tag(unprefixed_word):

                if not tag.is_productive():
                    continue

                if tag in seen_tags:
                    continue
                seen_tags.add(tag)

                res.append(tag)

        return res


class KnownSuffixPredictor(BasePredictor):
    """
    Parse the word by checking how the words with similar suffixes
    are parsed.
    """
    terminal = False
    ESTIMATE_DECAY = 0.5

    def __init__(self, morph):
        super(KnownSuffixPredictor, self).__init__(morph)

        self._paradigm_prefixes = list(reversed(list(enumerate(self.dict.paradigm_prefixes))))
        max_suffix_length = self.morph.dict_meta['prediction_options']['max_suffix_length']
        self._prediction_splits = list(reversed(range(1, max_suffix_length+1)))


    def parse(self, word, seen_parses=None):
        if seen_parses is None:
            seen_parses = set()

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
                    for cnt, para_id, idx in parses:

                        tag = self.dict.build_tag_info(para_id, idx)

                        if not tag.is_productive():
                            continue

                        total_counts[prefix_id] += cnt

                        fixed_word = word[:-i] + fixed_suffix
                        normal_form = self.dict.build_normal_form(para_id, idx, fixed_word)

                        parse = (cnt, fixed_word, tag, normal_form, para_id, idx, prefix_id)
                        reduced_parse = parse[1:4]
                        if reduced_parse in seen_parses:
                            continue

                        result.append(parse)

                if total_counts[prefix_id] > 1:
                    break

        result = [
            (fixed_word, tag, normal_form, para_id, idx, cnt/total_counts[prefix_id] * self.ESTIMATE_DECAY)
            for (cnt, fixed_word, tag, normal_form, para_id, idx, prefix_id) in result
        ]
        result.sort(key=operator.itemgetter(5), reverse=True)
        return result


    def tag(self, word, seen_tags=None):
        # XXX: the result order may be different from
        # ``self.parse(...)``.

        if seen_tags is None:
            seen_tags = set()

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
