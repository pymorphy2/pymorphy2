# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import os
import collections
import logging
import json
import struct
import array

import dawg

logger = logging.getLogger(__name__)

POSSIBLE_PREFIXES = ["", 'ПО', 'НАИ']

DictTuple = collections.namedtuple('DictTuple', 'meta gramtab suffixes paradigms words')

#class Dictionary(object):
#    def __init__(self, meta, gramtab, paradigms, words):
#        self.meta = meta
#        self.gramtab = gramtab
#        self.paradigms = paradigms
#        self.words = words


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

    with open(_f('suffixes.json'), 'r') as f:
        suffixes = json.load(f)

    paradigms = []
    with open(_f('paradigms.array'), 'rb') as f:
        paradigms_count = struct.unpack(str("<H"), f.read(2))[0]

        for x in range(paradigms_count):
            paradigm_len = struct.unpack(str("<H"), f.read(2))[0]
            para = array.array(str("H"))
            para.fromfile(f, paradigm_len)
            paradigms.append(para)

    words = WordsDawg().load(_f('words.dawg'))
    return DictTuple(meta, gramtab, suffixes, paradigms, words)
