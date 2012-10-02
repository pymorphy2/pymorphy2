# -*- coding: utf-8 -*-
"""
Utils for working with grammatical tags.
"""
from __future__ import absolute_import

def get_POS(tag):
    return tag.replace(' ', ',', 1).split(',', 1)[0]
