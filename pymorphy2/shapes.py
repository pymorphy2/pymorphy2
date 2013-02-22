# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unicodedata

_latin_letters_cache={}
def is_latin_letter(uchr):
    try:
        return _latin_letters_cache[uchr]
    except KeyError:
        if isinstance(uchr, bytes):
            uchr = uchr.decode('ascii')
        is_latin = 'LATIN' in unicodedata.name(uchr)
        return _latin_letters_cache.setdefault(uchr, is_latin)

def is_latin(word):
    """
    Return True if all word letters are latin and there is at
    least one latin letter in a word::

        >>> is_latin('foo')
        True
        >>> is_latin('123-FOO')
        True
        >>> is_latin('123')
        False
        >>> is_latin(':)')
        False

    """
    return (
        any(ch.isalpha() for ch in word) and
        all(is_latin_letter(ch) for ch in word if ch.isalpha())
    )
