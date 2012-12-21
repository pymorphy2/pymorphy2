# -*- coding: utf-8 -*-
from __future__ import absolute_import
import bz2
import os
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

