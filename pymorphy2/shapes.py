# -*- coding: utf-8 -*-
from __future__ import absolute_import
# unicode_literals future import is not needed and breaks 2.x tests

import unicodedata


_latin_letters_cache = {}
def is_latin_char(uchr):
    try:
        return _latin_letters_cache[uchr]
    except KeyError:
        if isinstance(uchr, bytes):
            uchr = uchr.decode('ascii')
        is_latin = 'LATIN' in unicodedata.name(uchr)
        return _latin_letters_cache.setdefault(uchr, is_latin)


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
        >>> is_latin('')
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


def restore_word_case(word, example):
    """
    Make the ``word`` be the same case as an ``example``::

        >>> restore_word_case('bye', 'Hello')
        'Bye'
        >>> restore_word_case('half-an-hour', 'Minute')
        'Half-An-Hour'
        >>> restore_word_case('usa', 'IEEE')
        'USA'
        >>> restore_word_case('pre-world', 'anti-World')
        'pre-World'
        >>> restore_word_case('123-do', 'anti-IEEE')
        '123-DO'
        >>> restore_word_case('123--do', 'anti--IEEE')
        '123--DO'

    In the alignment fails, the reminder is lower-cased::

        >>> restore_word_case('foo-BAR-BAZ', 'Baz-Baz')
        'Foo-Bar-baz'
        >>> restore_word_case('foo', 'foo-bar')
        'foo'

    """
    if '-' in example:
        results = []
        word_parts = word.split('-')
        example_parts = example.split('-')

        for i, part in enumerate(word_parts):
            if len(example_parts) > i:
                results.append(_make_the_same_case(part, example_parts[i]))
            else:
                results.append(part.lower())

        return '-'.join(results)

    return _make_the_same_case(word, example)


def _make_the_same_case(word, example):
    if example.islower():
        return word.lower()
    elif example.isupper():
        return word.upper()
    elif example.istitle():
        return word.title()
    else:
        return word.lower()
