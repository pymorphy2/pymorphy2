# -*- coding: utf-8 -*-
from __future__ import absolute_import
# unicode_literals here would break tests

import bz2
import os
import itertools
import codecs
import json

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

CHUNK_SIZE = 256*1024


def download_bz2(url, out_fp, chunk_size=CHUNK_SIZE, on_chunk=lambda: None):
    """
    Download a bz2-encoded file from ``url`` and write it to ``out_fp`` file.
    """
    decompressor = bz2.BZ2Decompressor()
    fp = urlopen(url, timeout=30)

    while True:
        data = fp.read(chunk_size)
        if not data:
            break
        out_fp.write(decompressor.decompress(data))
        on_chunk()


def get_mem_usage():
    import psutil
    proc = psutil.Process(os.getpid())
    try:
        return proc.memory_info().rss
    except AttributeError:
        # psutil < 2.x
        return proc.get_memory_info()[0]


def combinations_of_all_lengths(it):
    """
    Return an iterable with all possible combinations of items from ``it``:

        >>> for comb in combinations_of_all_lengths('ABC'):
        ...     print("".join(comb))
        A
        B
        C
        AB
        AC
        BC
        ABC

    """
    return itertools.chain(
        *(itertools.combinations(it, num+1) for num in range(len(it)))
    )


def longest_common_substring(data):
    """
    Return a longest common substring of a list of strings:

        >>> longest_common_substring(["apricot", "rice", "cricket"])
        'ric'
        >>> longest_common_substring(["apricot", "banana"])
        'a'
        >>> longest_common_substring(["foo", "bar", "baz"])
        ''

    See http://stackoverflow.com/questions/2892931/.
    """
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr) and all(data[0][i:i+j] in x for x in data):
                    substr = data[0][i:i+j]
    return substr


def json_write(filename, obj, **json_options):
    """ Create file ``filename`` with ``obj`` serialized to JSON """

    json_options.setdefault('ensure_ascii', False)
    with codecs.open(filename, 'w', 'utf8') as f:
        json.dump(obj, f, **json_options)


def json_read(filename, **json_options):
    """ Read an object from a json file ``filename`` """
    with codecs.open(filename, 'r', 'utf8') as f:
        return json.load(f, **json_options)


def largest_group(iterable, key):
    """
    Find a group of largest elements (according to ``key``).

    >>> s = [-4, 3, 5, 7, 4, -7]
    >>> largest_group(s, abs)
    [7, -7]

    """
    it1, it2 = itertools.tee(iterable)
    max_key = max(map(key, it1))
    return [el for el in it2 if key(el) == max_key]


def word_splits(word, min_reminder=3, max_prefix_length=5):
    """
    Return all splits of a word (taking in account min_reminder and
    max_prefix_length).
    """
    max_split = min(max_prefix_length, len(word)-min_reminder)
    split_indexes = range(1, 1+max_split)
    return [(word[:i], word[i:]) for i in split_indexes]
