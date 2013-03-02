# -*- coding: utf-8 -*-
"""
Analyzer units for unknown words with hyphens
---------------------------------------------
"""

from __future__ import absolute_import, unicode_literals, division

from pymorphy2.units.base import BaseAnalyzerUnit
from pymorphy2.units.utils import add_parse_if_not_seen, add_tag_if_not_seen


class HyphenSeparatedParticleAnalyzer(BaseAnalyzerUnit):
    """
    Parse the word by analyzing it without
    a particle after a hyphen.

    Example: смотри-ка -> смотри + "-ка".

    .. note::

        This analyzer doesn't remove particles from the result
        so for normalization you may need to handle
        particles at tokenization level.

    """
    terminal = True
    ESTIMATE_DECAY = 0.9

    # XXX: maybe the code can be made faster by compiling this list to a DAWG?
    PARTICLES_AFTER_HYPHEN = [
        "-то", "-ка", "-таки", "-де", "-тко", "-тка", "-с", "-ста"
    ]

    def get_lexeme(self, form, methods):
        particle = methods[-1][1]

        return list(
            self._suffixed_lexeme(
                super(HyphenSeparatedParticleAnalyzer, self).get_lexeme(
                    self._unsuffixed_form(form, particle),
                    methods
                ),
                particle
            )
        )

    def _suffixed_lexeme(self, lexeme, suffix):
        for p in lexeme:
            word, tag, normal_form, para_id, idx, estimate, methods = p
            yield (word+suffix, tag, normal_form+suffix,
                   para_id, idx, estimate, methods)

    def _unsuffixed_form(self, form, suffix):
        word, tag, normal_form, para_id, idx, estimate, methods = form
        return (word[:-len(suffix)], tag, normal_form[:-len(suffix)],
                para_id, idx, estimate, methods)


    def parse(self, word, seen_parses):

        result = []
        for particle in self.PARTICLES_AFTER_HYPHEN:
            if not word.endswith(particle):
                continue

            unsuffixed_word = word[:-len(particle)]
            if not unsuffixed_word:
                continue

            method = (self, particle)

            for fixed_word, tag, normal_form, para_id, idx, estimate, methods in self.morph.parse(unsuffixed_word):
                parse = (
                    fixed_word+particle, tag, normal_form+particle,
                    para_id, idx, estimate*self.ESTIMATE_DECAY,
                    methods+(method,)
                )
                add_parse_if_not_seen(parse, result, seen_parses)

            # If a word ends with with one of the particles,
            # it can't ends with an another.
            break

        return result


    def tag(self, word, seen_tags):
        result = []
        for particle in self.PARTICLES_AFTER_HYPHEN:
            if not word.endswith(particle):
                continue

            unsuffixed_word = word[:-len(particle)]
            if not unsuffixed_word:
                continue

            result.extend(self.morph.tag(unsuffixed_word))

            # If a word ends with with one of the particles,
            # it can't ends with an another.
            break

        return result


class HyphenatedWordsAnalyzer(HyphenSeparatedParticleAnalyzer):
    """
    Parse the word by parsing its hyphen-separated parts.

    Examples:

        * интернет-магазин -> "интернет-" + магазин
        * человек-гора -> человек + гора

    """

    terminal = True
    ESTIMATE_DECAY = 0.75

    def _similarity_features(self, tag):
        """
        @type tag: pymorphy2.tagset.OpencorporaTag
        """
        return (tag.POS, tag.number, tag.case, tag.person, tag.tense)

    def parse(self, word, seen_parses):
        if '-' not in word:
            return []

        result = []

        # If there are more than 2 parts, the rest would be parsed
        # by recursion.
        left, right = word.split('-', 1)

        left_parses = self.morph.parse(left)
        right_parses = self.morph.parse(right)

        # Step 1: Assume that the left part is an uninflected prefix.
        # Examples: интернет-магазин, воздушно-капельный
        method1 = (self, right)
        right_features = []

        for fixed_word, tag, normal_form, para_id, idx, estimate, methods in right_parses:
            parse = (
                '-'.join([left, fixed_word]), tag, '-'.join([left, normal_form]),
                para_id, idx, estimate*self.ESTIMATE_DECAY,
                methods+(method1,)
            )
            add_parse_if_not_seen(parse, result, seen_parses)
            right_features.append(self._similarity_features(tag))

        # Step 2: if left and right can be parsed the same way,
        # then it may be the case that both parts should be inflected.
        # Examples: человек-гора, команд-участниц, компания-производитель

        method2 = (self, word)

        # FIXME: quadratic algorithm
        for left_parse in left_parses:

            left_feat = self._similarity_features(left_parse[1])

            for parse_index, right_parse in enumerate(right_parses):
                right_feat = right_features[parse_index]

                if left_feat != right_feat:
                    continue

                # tag
                parse = (
                    '-'.join([left_parse[0], right_parse[0]]), # word
                    left_parse[1], # tag is from the left part
                    '-'.join([left_parse[2], right_parse[2]]),  # normal form
                    left_parse[3], left_parse[4], # para_id, idx?
                    left_parse[5]*self.ESTIMATE_DECAY,
                    left_parse[6]+(method2,)
                )
                add_parse_if_not_seen(parse, result, seen_parses)

        return result

    def tag(self, word, seen_tags):
        result = []
        for p in self.parse(word, set()):
            add_tag_if_not_seen(p[1], result, seen_tags)
        return result

