# -*- coding: utf-8 -*-
import re
GROUPING_SPACE_REGEX = re.compile('([^\w_-]|[+])', re.U)

def simple_word_tokenize(text):
    """
    Split text into tokens. Don't split by hyphen.
    """
    return [t for t in GROUPING_SPACE_REGEX.split(text)
            if t and not t.isspace()]
