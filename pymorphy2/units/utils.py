# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division

def add_parse_if_not_seen(parse, result_list, seen_parses):
    reduced_parse = parse[:3]
    if reduced_parse in seen_parses:
        return
    seen_parses.add(reduced_parse)
    result_list.append(parse)

def add_tag_if_not_seen(tag, result_list, seen_tags):
    if tag in seen_tags:
        return
    seen_tags.add(tag)
    result_list.append(tag)
