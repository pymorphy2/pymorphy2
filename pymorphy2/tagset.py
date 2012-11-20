# -*- coding: utf-8 -*-
"""
Utils for working with grammatical tags.

"""
from __future__ import absolute_import, unicode_literals
import collections

try:
    from sys import intern
except ImportError: # python 2.x has builtin ``intern`` function
    pass
    #intern = lambda x: x

# Design note: Tag objects should be immutable.
class OpencorporaTag(object):

    __slots__ = ['grammemes', '_lemma_grammemes', '_grammemes_set_cache', '_str']

    FORMAT = 'opencorpora-int'
    NON_PRODUCTIVE_CLASSES = set(['NUMR', 'NPRO', 'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ'])

    # XXX: is it a good idea to have these rules?
    EXTRA_INCOMPATIBLE = {
        'plur': set(['GNdr']),

        # XXX: how to use rules from OpenCorpora
        # (they have "lemma/form" separation)?

#        'anim': set(['femn', 'neut']),
#        'inan': set(['femn', 'neut']),
#        'ADJF': set(['voct', 'gen2', 'acc2', 'loc2']),
#        'PRTF': set(['voct', 'gen2', 'acc2', 'loc2']),
#        'GRND': set(['PErs', 'futr', 'GNdr']),
#        'Impe': set(['PErs', 'tran', 'Mult', 'impr', 'plur', 'masc', 'femn']),
#        'impf': set(['futr', 'incl']),
#        'perf': set(['pres', 'Mult']),
#        'Sgtm': set(['plur']),
#        'Pltm': set(['sing']),
#        'pssv': set(['intr']),

#        'past': set(['PErs']),
#        'futr': set(['PErs', 'GNdr']),
#        'pres': set(['GNdr']),
    }

    GRAMMEME_INDICES = collections.defaultdict(lambda: 0)
    GRAMMEME_INCOMPATIBLE = collections.defaultdict(set)

    def __init__(self, tag=None, grammemes=None, lemma_grammemes=1):
        if tag is not None:
            lemma_grammemes = tag.split(' ')[0].count(',') + 1
            grammemes = tag.replace(' ', ',', 1).split(',')
            self._str = tag
        else:
            grammemes = sorted(grammemes, key=lambda g: self.GRAMMEME_INDICES[g])
            self._str = None

        self._lemma_grammemes = lemma_grammemes # number of lemma grammemes
        self._grammemes_set_cache = None # cache

        # hacks for better memory usage (they save 1M..3M):
        # - use byte strings for grammemes under Python 2.x;
        # - grammemes are interned.
        self.grammemes = tuple([intern(str(g)) for g in grammemes])


    @property
    def _grammemes_set(self):
        """
        Tag grammemes as frozenset.
        """
        if self._grammemes_set_cache is None:
            self._grammemes_set_cache = frozenset(self.grammemes)
        return self._grammemes_set_cache

    @property
    def cls(self):
        """
        Word class (as string).
        """
        return self.grammemes[0]

    def is_productive(self):
        return not self.cls in self.NON_PRODUCTIVE_CLASSES

    def _updated(self, add):
        """
        Returns a new OpencorporaTag with grammemes from ``add`` added
        and incompatible grammemes removed.
        """
        new_grammemes = self._grammemes_set | set(add)
        for grammeme in add:
            new_grammemes -= self.GRAMMEME_INCOMPATIBLE[grammeme]

        # XXX: lemma_grammemes would be incorrect, but this shouldn't matter
        # because tags constructed with "_updated" method should be for
        # internal use only.
        return OpencorporaTag(grammemes=new_grammemes)

    # FIXME: __repr__ and __str__ always return unicode,
    # but they should return a byte string under Python 2.x.
    def __str__(self):
        if self._str is None:
            lemma_tags = ",".join(self.grammemes[:self._lemma_grammemes])
            form_tags = ",".join(self.grammemes[self._lemma_grammemes:])
            if not form_tags:
                self._str = lemma_tags
            else:
                self._str = lemma_tags + " " + form_tags
        return self._str

    def __repr__(self):
        return "OpencorporaTag('%s')" % self


    def __eq__(self, other):
        return self.grammemes == other.grammemes

    def __ne__(self, other):
        return self.grammemes != other.grammemes

    def __lt__(self, other):
        return self.grammemes < other.grammemes

    def __gt__(self, other):
        return self.grammemes > other.grammemes

    def __hash__(self):
        return hash(self.grammemes)

    @classmethod
    def _init_restrictions(cls, grammemes):
        """
        Fills ``OpencorporaTag.GRAMMEME_INDICES`` and
        ``OpencorporaTag.GRAMMEME_INCOMPATIBLE`` class attributes.
        """

        # figure out parents & children
        gr = dict(grammemes)
        children = collections.defaultdict(set)

        for index, (name, parent) in enumerate(grammemes):
            if parent:
                children[parent].add(name)
            if gr.get(parent, None): # parent's parent
                children[gr[parent]].add(name)

        # expand EXTRA_INCOMPATIBLE
        for grammeme, g_set in cls.EXTRA_INCOMPATIBLE.items():
            for g in g_set.copy():
                g_set.update(children[g])

        # fill GRAMMEME_INDICES and GRAMMEME_INCOMPATIBLE
        for index, (name, parent) in enumerate(grammemes):
            cls.GRAMMEME_INDICES[name] = index
            incompatible = cls.EXTRA_INCOMPATIBLE.get(name, set())
            incompatible = (incompatible | children[parent]) - set([name])

            cls.GRAMMEME_INCOMPATIBLE[name] = frozenset(incompatible)


registry = dict()

for tag_type in [OpencorporaTag, ]:
    registry[tag_type.FORMAT] = tag_type