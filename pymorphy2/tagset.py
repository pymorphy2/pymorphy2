# -*- coding: utf-8 -*-
"""
Utils for working with grammatical tags.
"""
from __future__ import absolute_import, unicode_literals
import collections

try:
    from sys import intern
except ImportError:
    # python 2.x has builtin ``intern`` function
    pass


# Design notes: Tag objects should be immutable.
class InternalOpencorporaTag(object):

    __slots__ = ['_grammemes_tuple', '_lemma_grammemes', '_grammemes_cache', '_str']

    FORMAT = 'opencorpora-int'
    NON_PRODUCTIVE_CLASSES = set(['NUMR', 'NPRO', 'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ'])

    # XXX: is it a good idea to have these rules?
    EXTRA_INCOMPATIBLE = {
        'plur': set(['GNdr']),
        # XXX: how to use rules from OpenCorpora
        # (they have "lemma/form" separation)?
    }
    GRAMMEME_INDICES = collections.defaultdict(lambda: 0)
    GRAMMEME_INCOMPATIBLE = collections.defaultdict(set)

    def __init__(self, tag):
        self._str = tag

        # XXX: we loose information about which grammemes
        # belongs to lemma and which belongs to form
        # (this information seems useless for pymorphy2).

        # Hacks for better memory usage:
        # - store grammemes in a tuple and build a set only when needed;
        # - use byte strings for grammemes under Python 2.x;
        # - grammemes are interned.
        grammemes = tag.replace(' ', ',', 1).split(',')
        self._grammemes_tuple = tuple([intern(str(g)) for g in grammemes])
        self._grammemes_cache = None

    @property
    def grammemes(self):
        """
        Tag grammemes as frozenset.
        """
        if self._grammemes_cache is None:
            self._grammemes_cache = frozenset(self._grammemes_tuple)
        return self._grammemes_cache

    @property
    def cls(self):
        """
        Word class (as string).
        """
        return self._grammemes_tuple[0]

    def is_productive(self):
        return not self.cls in self.NON_PRODUCTIVE_CLASSES

    def updated_grammemes(self, required):
        """
        Returns a new set of grammemes with ``required`` grammemes added
        and incompatible grammemes removed.
        """
        new_grammemes = self.grammemes | required
        for grammeme in required:
            if grammeme not in self.GRAMMEME_INDICES:
                raise ValueError("Unknown grammeme: %s" % grammeme)
            new_grammemes -= self.GRAMMEME_INCOMPATIBLE[grammeme]
        return new_grammemes

    # FIXME: __repr__ and __str__ always return unicode,
    # but they should return a byte string under Python 2.x.
    def __str__(self):
        return self._str

    def __repr__(self):
        return "OpencorporaTag('%s')" % self


    def __eq__(self, other):
        return self._grammemes_tuple == other._grammemes_tuple

    def __ne__(self, other):
        return self._grammemes_tuple != other._grammemes_tuple

    def __lt__(self, other):
        return self._grammemes_tuple < other._grammemes_tuple

    def __gt__(self, other):
        return self._grammemes_tuple > other._grammemes_tuple

    def __hash__(self):
        return hash(self._grammemes_tuple)


    @classmethod
    def _from_internal_tag(cls, tag):
        """ Returns tag string given internal tag string """
        return tag

    @classmethod
    def _from_internal_grammeme(cls, grammeme):
        return grammeme


    @classmethod
    def _init_restrictions(cls, dict_grammemes):
        """
        Fills ``OpencorporaTag.GRAMMEME_INDICES`` and
        ``OpencorporaTag.GRAMMEME_INCOMPATIBLE`` class attributes.
        """

        # figure out parents & children
        gr = dict(((name, parent) for (name, parent, alias, description) in dict_grammemes))
        children = collections.defaultdict(set)

        for index, (name, parent, alias, description) in enumerate(dict_grammemes):
            if parent:
                children[parent].add(name)
            if gr.get(parent, None): # parent's parent
                children[gr[parent]].add(name)

        # expand EXTRA_INCOMPATIBLE
        for grammeme, g_set in cls.EXTRA_INCOMPATIBLE.items():
            for g in g_set.copy():
                g_set.update(children[g])

        # fill GRAMMEME_INDICES and GRAMMEME_INCOMPATIBLE
        for index, (name, parent, alias, description) in enumerate(dict_grammemes):
            cls.GRAMMEME_INDICES[name] = index
            incompatible = cls.EXTRA_INCOMPATIBLE.get(name, set())
            incompatible = (incompatible | children[parent]) - set([name])

            cls.GRAMMEME_INCOMPATIBLE[name] = frozenset(incompatible)


class OpencorporaTag(InternalOpencorporaTag):
    FORMAT = 'opencorpora-ext'
    GRAMMEME_ALIAS_MAP = dict()

    @classmethod
    def _from_internal_tag(cls, tag):
        for name, alias in cls.GRAMMEME_ALIAS_MAP.items():
            if alias:
                tag = tag.replace(name, alias)
        return tag

    @classmethod
    def _from_internal_grammeme(cls, grammeme):
        return cls.GRAMMEME_ALIAS_MAP.get(grammeme, grammeme)

    @classmethod
    def _init_restrictions(cls, dict_grammemes):
        """
        Fills ``OpencorporaTag.GRAMMEME_INDICES`` and
        ``OpencorporaTag.GRAMMEME_INCOMPATIBLE`` class attributes.
        """
        cls._init_alias_map(dict_grammemes)
        super(OpencorporaTag, cls)._init_restrictions(dict_grammemes)

        GRAMMEME_INDICES = collections.defaultdict(lambda: 0)
        for name, idx in cls.GRAMMEME_INDICES.items():
            GRAMMEME_INDICES[cls._from_internal_grammeme(name)] = idx
        cls.GRAMMEME_INDICES = GRAMMEME_INDICES

        GRAMMEME_INCOMPATIBLE = collections.defaultdict(set)
        for name, value in cls.GRAMMEME_INCOMPATIBLE.items():
            GRAMMEME_INCOMPATIBLE[cls._from_internal_grammeme(name)] = set([
                cls._from_internal_grammeme(gr) for gr in value
            ])
        cls.GRAMMEME_INCOMPATIBLE = GRAMMEME_INCOMPATIBLE

        cls.NON_PRODUCTIVE_CLASSES = set([
            cls._from_internal_grammeme(gr) for gr in cls.NON_PRODUCTIVE_CLASSES
        ])


    @classmethod
    def _init_alias_map(cls, dict_grammemes):
        for name, parent, alias, description in dict_grammemes:
            cls.GRAMMEME_ALIAS_MAP[name] = alias



registry = dict()

for tag_type in [OpencorporaTag, InternalOpencorporaTag]:
    registry[tag_type.FORMAT] = tag_type