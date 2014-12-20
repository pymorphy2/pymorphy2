# -*- coding: utf-8 -*-

from pymorphy2.units import DictionaryAnalyzer
from pymorphy2.units.base import AnalogyAnalizerUnit
from pymorphy2.units.utils import add_parse_if_not_seen, add_tag_if_not_seen

import re


#
# class NumberWithCaseAnalyzer(_ShapeAnalyzer):
#     """
#     This analyzer marks integer numbers with "NUMB,int" tags.
#     Example: "12" -> NUMB,int;
#
#     .. note::
#
#         Don't confuse it with "NUMR": "тридцать" -> NUMR
#
#     """
#     EXTRA_GRAMMEMES = ['NUMB']
#     EXTRA_GRAMMEMES_CYR = ['ЧИСЛО']
#
#     def check_shape(self, word, word_lower):
#         try:
#
#             int(word)
#             return True
#         except ValueError:
#             return False
#
#
#         #
#         # def get_tag(self, word, shape):
#         #     return self.[shape]


class NumberWithCaseAnalyzer(AnalogyAnalizerUnit):
    """
    Works by using analogy with adj.

    Example:
    1-ый <-> умный
    2-ой <-> родной
    2-ий <-> крайний
    """

    def __init__(self, morph):
        super(NumberWithCaseAnalyzer, self).__init__(morph)
        self.dict_analyzer = DictionaryAnalyzer(morph)

    def parse(self, word, word_lower, seen_parses):
        result = []

        numb_re = r'(\d+)(-?)(\w+)'
        match = re.match(numb_re, word_lower)
        if match is not None:
            for adj in ['умный', 'родной', 'крайний']:
                prefix_adj = adj[:-2]
                prefix_numb = ''.join(match.group(1, 2))

                method = (self, adj)

                parses = self.dict_analyzer.parse(adj, adj, seen_parses)
                for fixed_word, tag, normal_form, score, methods_stack in parses:

                    if not tag.is_productive():
                        continue

                    parse = (
                        fixed_word.replace(prefix_adj, prefix_numb, 1),
                        tag,
                        normal_form.replace(prefix_adj, prefix_numb, 1),
                        score * self.ESTIMATE_DECAY,
                        methods_stack + (method,)
                    )
                    add_parse_if_not_seen(parse, result, seen_parses)

        return result

    def tag(self, word, word_lower, seen_tags):
        result = []

        numb_re = r'(\d+)(-?)(\w+)'
        match = re.match(numb_re, word_lower)
        if match is not None:
            for adj in ['умный', 'родной', 'крайний']:
                # prefix_adj = adj[:-2]
                # prefix_numb = ''.join(match.group(1, 2))

                tags = self.dict_analyzer.tag(adj, adj, seen_tags)
                for tag in tags:

                    if not tag.is_productive():
                        continue

                    add_tag_if_not_seen(tag, result, seen_tags)

        return result
