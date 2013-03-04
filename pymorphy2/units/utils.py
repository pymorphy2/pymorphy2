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


def with_suffix(form, suffix):
    """ Return a new form with ``suffix`` attached """
    word, tag, normal_form, para_id, idx, estimate, methods_stack = form
    return (word+suffix, tag, normal_form+suffix, para_id, idx, estimate, methods_stack)


def without_suffix(form, suffix):
    """ Return a new form with ``suffix`` removed """
    word, tag, normal_form, para_id, idx, estimate, methods_stack = form
    return (word[:-len(suffix)], tag, normal_form[:-len(suffix)],
            para_id, idx, estimate, methods_stack)
