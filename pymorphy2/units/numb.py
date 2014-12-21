# -*- coding: utf-8 -*-
from pymorphy2.tagset import OpencorporaTag
from pymorphy2.units import DictionaryAnalyzer
from pymorphy2.units.base import AnalogyAnalizerUnit
from pymorphy2.units.utils import add_parse_if_not_seen, add_tag_if_not_seen

import re


class NumberWithCaseAnalyzer(AnalogyAnalizerUnit):
    """
    Works by using analogy with adj.

    Example:
    1-ый <-> умный
    2-ой <-> родной
    2-ий <-> крайний
    """

    ESTIMATE_DECAY = 0.9
    SUFFIXES = u'ая его ее ей ем ему ею и ие ий им ими их ого ое ой ом ому ою ую ые ый ым ыми ых юю я яя'.split()
    NUMB_RE = re.compile(r'(\d+)(-?)(\w{1,3})')

    def __init__(self, morph):
        super(NumberWithCaseAnalyzer, self).__init__(morph)
        self.dict_analyzer = DictionaryAnalyzer(morph)

    def _good(self, tag):
        return tag.is_productive() and tag.POS == 'ADJF'

    def _fix_tag(self, tag):
        # FIXME: how to do this correctly?
        return OpencorporaTag(str(tag).replace('ADJF', 'NUMB').replace('Qual ', ''))

    def _adj_like_numb(self, word):
        match = self.NUMB_RE.match(word)
        if match is not None:
            for adj in [u'умный', u'родной', u'крайний']:
                adj_prefix, adj_suffix = adj[:-2], adj[-2:]
                numb_prefix, numb_suffix = ''.join(match.group(1, 2)), match.group(3)

                method = (self, adj)

                for suffix in self.SUFFIXES:
                    if suffix.endswith(numb_suffix):
                        adj_like_numb = adj_prefix + suffix
                        if self.morph.word_is_known(adj_like_numb):
                            yield adj_like_numb, adj_prefix, numb_prefix, method

    def parse(self, word, word_lower, seen_parses):
        result = []
        for adj_like_numb, adj_prefix, numb_prefix, method in self._adj_like_numb(word_lower):
            parses = self.dict_analyzer.parse(adj_like_numb, adj_like_numb, seen_parses)
            for fixed_word, tag, normal_form, score, methods_stack in parses:
                if self._good(tag):
                    parse = (
                        fixed_word.replace(adj_prefix, numb_prefix, 1),
                        self._fix_tag(tag),
                        normal_form.replace(adj_prefix, numb_prefix, 1),
                        score * self.ESTIMATE_DECAY,
                        methods_stack + (method,)
                    )
                    add_parse_if_not_seen(parse, result, seen_parses, compare_by_tag=True)
        return result

    def tag(self, word, word_lower, seen_tags):
        result = []
        for adj_like_numb, adj_prefix, numb_prefix, method in self._adj_like_numb(word_lower):
            tags = self.dict_analyzer.tag(adj_like_numb, adj_like_numb, seen_tags)
            for tag in tags:
                if self._good(tag):
                    add_tag_if_not_seen(tag, result, seen_tags)
        return result
