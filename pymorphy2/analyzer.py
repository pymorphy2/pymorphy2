# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import os
import heapq
import collections
from pymorphy2 import opencorpora_dict

Parse = collections.namedtuple('Parse', 'word, tag, normal_form, para_id, idx, estimate')

class MorphAnalyzer(object):
    """
    Morphological analyzer for Russian language.

    For a given word it can find all possible inflectional paradigms
    and thus compute all possible tags and normal forms.

    Analyzer uses morphological word features and a lexicon
    (dictionary compiled from XML available at OpenCorpora.org);
    for unknown words heuristic algorithm is used.
    """

    env_variable = 'PYMORPHY2_DICT_PATH'

    def __init__(self, path=None, result_type=Parse):
        """
        Create a MorphAnalyzer object using dictionaries at ``path``.

        If ``path`` is None then the path is obtained from
        ``PYMORPHY2_DICT_PATH`` environment variable.

        By default, methods of this class return parsing results
        as namedtuples ``Parse``. This has performance implications
        under CPython, so if you need maximum speed then pass
        ``result_type=None`` to make analyzer return plain unwrapped tuples.
        """

        if path is None:
            if self.env_variable not in os.environ:
                raise ValueError("Please pass a path to dictionaries or set "
                                 "%s environment variable" % self.env_variable)
            path = os.environ[self.env_variable]

        self._dictionary = opencorpora_dict.load(path)
        self._ee = self._dictionary.words.compile_replaces({'е': 'ё'})
        self._result_type = result_type


    def parse(self, word):
        """
        Analyze the word and return a list of

            Parse(word, tag, normal_form, _para_id, _idx, _estimate)

        namedtuples (or plain tuples if ``result_type=None`` was used
        in constructor).
        """
        res = self._parse_as_known(word)
        if not res:
            res = self._parse_as_word_with_known_prefix(word)
        if not res:
            seen = set()
            res = self._parse_as_word_with_unknown_prefix(word, seen)
            res.extend(self._parse_as_word_with_known_suffix(word, seen))

        if self._result_type is None:
            return res

        return [self._result_type(*p) for p in res]

    def _parse_as_known(self, word):
        """
        Parse the word using a dictionary.
        """
        res = []
        para_normal_forms = {}
        para_data = self._dictionary.words.similar_items(word, self._ee)

        for fixed_word, parses in para_data:
            # `fixed_word` is a word with proper ё letters
            for para_id, idx in parses:

                if para_id not in para_normal_forms:
                    normal_form = self._build_normal_form(para_id, idx, fixed_word)
                    para_normal_forms[para_id] = normal_form
                else:
                    normal_form = para_normal_forms[para_id]

                tag = self._build_tag_info(para_id, idx)

                res.append(
                    (fixed_word, tag, normal_form, para_id, idx, 1.0)
                )

        return res

    def _parse_as_word_with_known_prefix(self, word):
        """
        Parse the word by checking if it starts with a known prefix
        and parsing the reminder.
        """
        res = []
        ESTIMATE_DECAY = 0.75
        word_prefixes = self._dictionary.prediction_prefixes.prefixes(word)
        for prefix in word_prefixes:
            unprefixed_word = word[len(prefix):]

            for fixed_word, tag, normal_form, para_id, idx, estimate in self.parse(unprefixed_word):

                if not tag.is_productive():
                    continue

                parse = (prefix+fixed_word, tag, prefix+normal_form, para_id, idx, estimate*ESTIMATE_DECAY)
                res.append(parse)

        return res

    def _parse_as_word_with_unknown_prefix(self, word, _seen_parses=None):
        """
        Parse the word by parsing only the word suffix
        (with restrictions on prefix & suffix lengths).
        """
        if _seen_parses is None:
            _seen_parses = set()
        res = []
        ESTIMATE_DECAY = 0.5
        for prefix, unprefixed_word in _split_word(word):
            for fixed_word, tag, normal_form, para_id, idx, estimate in self._parse_as_known(unprefixed_word):

                if not tag.is_productive():
                    continue

                parse = (prefix+fixed_word, tag, prefix+normal_form, para_id, idx, estimate*ESTIMATE_DECAY)

                reduced_parse = parse[:3]
                if reduced_parse in _seen_parses:
                    continue
                _seen_parses.add(reduced_parse)

                res.append(parse)

        return res

    def _parse_as_word_with_known_suffix(self, word, _seen_parses=None):
        """
        Parse the word by checking how the words with similar suffixes
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
            for fixed_suffix, parses in para_data:
                for cnt, para_id, idx in parses:

                    tag = self._build_tag_info(para_id, idx)

                    if not tag.is_productive():
                        continue

                    total_cnt += cnt

                    fixed_word = word[:-i] + fixed_suffix
                    normal_form = self._build_normal_form(para_id, idx, fixed_word)

                    parse = (cnt, fixed_word, tag, normal_form, para_id, idx)
                    reduced_parse = parse[1:4]
                    if reduced_parse in _seen_parses:
                        continue

                    result.append(parse)

            if total_cnt > 1:
                # parses are sorted inside paradigms, but they are unsorted overall
                result.sort(reverse=True)
                result = [
                    (fixed_word, tag, normal_form, para_id, idx, cnt/total_cnt * ESTIMATE_DECAY)
                    for (cnt, fixed_word, tag, normal_form, para_id, idx) in result
                ]
                break

        return result

    def normal_forms(self, word):
        """
        Return a list of word normal forms.
        """
        seen = set()
        result = []
        for fixed_word, tag, normal_form, para_id, idx, estimate in self.parse(word):
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
            seen = set()
            res = self._tag_as_word_with_unknown_prefix(word, seen)
            res.extend(self._tag_as_word_with_known_suffix(word, seen))

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

            for tag in self.tag(unprefixed_word):
                if not tag.is_productive():
                    continue
                res.append(tag)

        return res

    def _tag_as_word_with_unknown_prefix(self, word, _seen_tags=None):
        if _seen_tags is None:
            _seen_tags = set()

        res = []
        for _, unprefixed_word in _split_word(word):
            for tag in self._tag_as_known(unprefixed_word):

                if not tag.is_productive():
                    continue

                if tag in _seen_tags:
                    continue
                _seen_tags.add(tag)

                res.append(tag)

        return res

    def _tag_as_word_with_known_suffix(self, word, _seen_tags=None):
        if _seen_tags is None:
            _seen_tags = set()

        result = []
        for i in 5,4,3,2,1:
            end = word[-i:]
            para_data = self._dictionary.prediction_suffixes.similar_item_values(end, self._ee)

            found = False
            for parse in para_data:
                for cnt, para_id, idx in parse:
                    tag = self._build_tag_info(para_id, idx)

                    if not tag.is_productive():
                        continue

                    found = True
                    if tag in _seen_tags:
                        continue

                    _seen_tags.add(tag)
                    result.append(
                        (cnt, tag)
                    )

            if found:
                result.sort(reverse=True)
                result = [tag for cnt, tag in result] # remove counts
                break

        return result

    # ==== inflection ========

    def inflect(self, word, required_grammemes):
        """
        Return a list of parsed words that are closest to ``word`` and
        have all ``required_grammemes``.
        """
        required_grammemes = set(required_grammemes)
        parses = self.parse(word)

        def weigth(parse):
            # order by (probability, index in lexeme)
            return -parse[5], parse[4]

        result = []
        seen = set()
        for form in sorted(parses, key=weigth):
            for inflected in self._inflect(form, required_grammemes):
                if inflected in seen:
                    continue
                seen.add(inflected)
                result.append(inflected)

        return result

    def _inflect(self, form, required_grammemes):
        grammemes = form[1].updated_grammemes(required_grammemes)

        possible_results = [form for form in self._decline([form])
                            if required_grammemes.issubset(form[1].grammemes)]

        def similarity(form):
            tag = form[1]
            return len(grammemes & tag.grammemes)

        return heapq.nlargest(1, possible_results, key=similarity)

    def decline(self, word):
        """
        Return parses for all possible word forms.
        """
        return self._decline(self.parse(word))

    def _decline(self, word_parses):
        """
        Return parses for all possible word forms (given a list of
        possible word parses).
        """
        paradigms = self._dictionary.paradigms
        seen_paradigms = set()
        result = []

        for fixed_word, tag, normal_form, para_id, idx, estimate in word_parses:
            if para_id in seen_paradigms:
                continue
            seen_paradigms.add(para_id)

            stem = self._build_stem(paradigms[para_id], idx, fixed_word)

            for index, (_prefix, _tag, _suffix) in enumerate(self._build_paradigm_info(para_id)):
                word = _prefix + stem + _suffix

                # XXX: what to do with estimate?
                # XXX: do we need all info?
                result.append(
                    (word, _tag, normal_form, para_id, index, estimate)
                )

        if self._result_type is None:
            return result

        return [self._result_type(*p) for p in result]


    # ==== dictionary access utilities ===

    def _build_tag_info(self, para_id, idx):
        """
        Return gram. tag as a string.
        """
        paradigm = self._dictionary.paradigms[para_id]
        tag_info_offset = len(paradigm) // 3
        tag_id = paradigm[tag_info_offset + idx]
        return self._dictionary.gramtab[tag_id]

    def _build_paradigm_info(self, para_id):
        """
        Return a list of

            (prefix, tag, suffix)

        tuples representing the paradigm.
        """
        paradigm = self._dictionary.paradigms[para_id]
        paradigm_len = len(paradigm) // 3
        res = []
        for idx in range(paradigm_len):
            prefix_id = paradigm[paradigm_len*2 + idx]
            prefix = self._dictionary.paradigm_prefixes[prefix_id]

            suffix_id = paradigm[idx]
            suffix = self._dictionary.suffixes[suffix_id]

            res.append(
                (prefix, self._build_tag_info(para_id, idx), suffix)
            )
        return res

    def _build_normal_form(self, para_id, idx, fixed_word):
        """
        Build a normal form.
        """

        if idx == 0: # a shortcut: normal form is a word itself
            return fixed_word

        paradigm = self._dictionary.paradigms[para_id]
        paradigm_len = len(paradigm) // 3

        stem = self._build_stem(paradigm, idx, fixed_word)

        normal_prefix_id = paradigm[paradigm_len*2 + 0]
        normal_suffix_id = paradigm[0]

        normal_prefix = self._dictionary.paradigm_prefixes[normal_prefix_id]
        normal_suffix = self._dictionary.suffixes[normal_suffix_id]

        return normal_prefix + stem + normal_suffix

    def _build_stem(self, paradigm, idx, fixed_word):
        """
        Return word stem (given a word, paradigm and the word index).
        """
        paradigm_len = len(paradigm) // 3

        prefix_id = paradigm[paradigm_len*2 + idx]
        prefix = self._dictionary.paradigm_prefixes[prefix_id]

        suffix_id = paradigm[idx]
        suffix = self._dictionary.suffixes[suffix_id]

        if suffix:
            return fixed_word[len(prefix):-len(suffix)]
        else:
            return fixed_word[len(prefix):]


    # ====== misc =========

    def word_is_known(self, word, strict_ee=False):
        """
        Check if a ``word`` is in the dictionary.
        Pass ``strict_ee=True`` if ``word`` is guaranteed to
        have correct е/ё letters.

        .. note::

            Dictionary words are not always correct words;
            the dictionary also contains incorrect forms which
            are commonly used. So for spellchecking tasks this
            method should be used with extra care.

        """
        if strict_ee:
            return word in self._dictionary.words
        else:
            return bool(self._dictionary.words.similar_keys(word, self._ee))

    def meta(self):
        return self._dictionary.meta

    @property
    def TagClass(self):
        return self._dictionary.Tag


def _split_word(word, min_reminder=3, max_prefix_length=5):
    """
    Return all splits of a word (taking in account min_reminder and
    max_prefix_length).
    """
    max_split = min(max_prefix_length, len(word)-min_reminder)
    split_indexes = range(1, 1+max_split)
    return [(word[:i], word[i:]) for i in split_indexes]
