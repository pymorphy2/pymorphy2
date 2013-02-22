# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unicodedata

def is_latin(token):
    """
    Return True if all token letters are latin and there is at
    least one latin letter in the token::

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
        any(ch.isalpha() for ch in token) and
        all(is_latin_char(ch) for ch in token if ch.isalpha())
    )

def is_punctuation(token):
    """
    Return True if a word contains only spaces and punctuation marks
    and there is at least one punctuation mark::

        >>> is_punctuation(', ')
        True
        >>> is_punctuation('..!')
        True
        >>> is_punctuation('x')
        False
        >>> is_punctuation(' ')
        False
        >>> is_punctuation('')
        False

    """
    if isinstance(token, bytes): # python 2.x ascii str
        token = token.decode('ascii')

    return (
        bool(token) and
        not token.isspace() and
        all(unicodedata.category(ch)[0] == 'P' for ch in token if not ch.isspace())
    )

_latin_letters_cache={}
def is_latin_char(uchr):
    try:
        return _latin_letters_cache[uchr]
    except KeyError:
        if isinstance(uchr, bytes):
            uchr = uchr.decode('ascii')
        is_latin = 'LATIN' in unicodedata.name(uchr)
        return _latin_letters_cache.setdefault(uchr, is_latin)
