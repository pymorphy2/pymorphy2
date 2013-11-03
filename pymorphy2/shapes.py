# -*- coding: utf-8 -*-
from __future__ import absolute_import
# unicode_literals future import is not needed and breaks 2.x tests

import re
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
    least one latin letter in the token:

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
    and there is at least one punctuation mark:

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
    if isinstance(token, bytes):  # python 2.x ascii str
        token = token.decode('ascii')

    return (
        bool(token) and
        not token.isspace() and
        all(unicodedata.category(ch)[0] == 'P' for ch in token if not ch.isspace())
    )


# The regex is from "Dive into Python" book.
ROMAN_NUMBERS_RE = re.compile("""
    M{0,4}              # thousands - 0 to 4 M's
    (CM|CD|D?C{0,3})    # hundreds - 900 (CM), 400 (CD), 0-300 (0 to 3 C's),
                        #            or 500-800 (D, followed by 0 to 3 C's)
    (XC|XL|L?X{0,3})    # tens - 90 (XC), 40 (XL), 0-30 (0 to 3 X's),
                        #        or 50-80 (L, followed by 0 to 3 X's)
    (IX|IV|V?I{0,3})    # ones - 9 (IX), 4 (IV), 0-3 (0 to 3 I's),
                        #        or 5-8 (V, followed by 0 to 3 I's)
    $                   # end of string
""", re.VERBOSE | re.IGNORECASE)

def is_roman_number(token):
    """
    Return True if token looks like a Roman number:

        >>> is_roman_number('II')
        True
        >>> is_roman_number('IX')
        True
        >>> is_roman_number('XIIIII')
        False
        >>> is_roman_number('')
        False

    """
    if not token:
        return False
    return re.match(ROMAN_NUMBERS_RE, token) is not None


def restore_word_case(word, example):
    """
    Make the ``word`` be the same case as an ``example``:

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

    In the alignment fails, the reminder is lower-cased:

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
