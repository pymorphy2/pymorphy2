# -*- coding: utf-8 -*-
from __future__ import absolute_import


def assert_parse_is_correct(parses, word, normal_form, tag):
    """
    Check if one of the word parses has normal form ``normal_form``
    and tag ``tag``.
    """
    for p in parses:
        if p.normal_form == normal_form and str(p.tag) == tag:
            return
    assert False, parses

