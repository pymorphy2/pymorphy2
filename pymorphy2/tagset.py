# -*- coding: utf-8 -*-
"""
Utils for working with grammatical tags.
"""
from __future__ import absolute_import, unicode_literals

class OpencorporaTag(object):

    __slots__ = ['_tag', '_tags_tuple']

    FORMAT = 'opencorpora-int'
    NON_PRODUCTIVE_CLASSES = set(['NUMR', 'NPRO', 'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ'])

    def __init__(self, tag):
        self._tag = tag
        self._tags_tuple = tuple(tag.replace(' ', ',', 1).split(','))

    def get_class(self):
        return self.parts()[0]

    def is_productive(self):
        return not self.get_class() in self.NON_PRODUCTIVE_CLASSES

    def parts(self):
        return self._tags_tuple

    def __repr__(self):
        # FIXME: this method always returns unicode,
        # but it should return a byte string under Python 2.x.
        return "OpencorporaTag('%s')" % self._tag

    def __eq__(self, other):
        return self._tags_tuple == other._tags_tuple

    def __ne__(self, other):
        return self._tags_tuple != other._tags_tuple

    def __gt__(self, other):
        return self._tags_tuple > other._tags_tuple

    def __lt__(self, other):
        return self._tags_tuple < other._tags_tuple

    def __hash__(self):
        return hash(self._tag)


registry = dict()

for tag_type in [OpencorporaTag, ]:
    registry[tag_type.FORMAT] = tag_type