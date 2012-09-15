# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import os
import collections
import logging
import json

import dawg

logger = logging.getLogger(__name__)

POSSIBLE_PREFIXES = ['ПО', 'по']

DictTuple = collections.namedtuple('DictTuple', 'meta gramtab paradigms words')

class WordsDawg(dawg.RecordDAWG):
    """
    DAWG for storing words.
    """

    # We are storing 2 unsigned short ints as values:
    # the paradigm ID and the form index (inside paradigm).
    # Byte order is big-endian (this makes word forms properly sorted).
    DATA_FORMAT = str(">HH")

    def __init__(self, data=None):
        super(WordsDawg, self).__init__(self.DATA_FORMAT, data)


def load_dict(path):
    """
    Loads Pymorphy2 dictionary.
    ``path`` is a folder name where dictionary data reside.
    """
    #meta, gramtab, paradigms, words = [None]*4

    _f = lambda p: os.path.join(path, p)

    with open(_f('meta.json'), 'r') as f:
        meta = json.load(f)

    if meta['version'] != 1:
        raise ValueError("This dictionary format is not supported")

    with open(_f('gramtab.json'), 'r') as f:
        gramtab = json.load(f)

    with open(_f('paradigms.json'), 'r') as f:
        paradigms = json.load(f)

    words = WordsDawg()
    words.load(_f('words.dawg'))
    return DictTuple(meta, gramtab, paradigms, words)
