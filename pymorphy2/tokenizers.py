# -*- coding: utf-8 -*-
import re

GROUPING_SPACE_REGEX = re.compile('([^\w_-]|[+])', re.U)


def simple_word_tokenize(text, _split=GROUPING_SPACE_REGEX.split):
    """ Split text into tokens. Don't split by a hyphen. """
    return [t for t in _split(text) if t and not t.isspace()]
