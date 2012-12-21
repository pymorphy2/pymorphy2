# -*- coding: utf-8 -*-
from __future__ import absolute_import
import bz2
import os
import itertools
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
    return proc.get_memory_info()[0]


def combinations_of_all_lengths(it):
    """
    Return an iterable with all possible combinations of items from ``it``::

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
    Return a longest common substring of a list of strings::

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
