# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division


def add_parse_if_not_seen(parse, result_list, seen_parses):
    para_id = parse[3][0][2]
    word = parse[0]
    tag = parse[1]

    reduced_parse = word, tag, para_id

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
    word, tag, estimate, methods_stack = form
    return (word+suffix, tag, estimate, methods_stack)


def without_fixed_suffix(form, suffix_length):
    """ Return a new form with ``suffix_length`` chars removed from right """
    word, tag, estimate, methods_stack = form
    return (word[:-suffix_length], tag, estimate, methods_stack)


def without_fixed_prefix(form, prefix_length):
    """ Return a new form with ``prefix_length`` chars removed from left """
    word, tag, estimate, methods_stack = form
    return (word[prefix_length:], tag, estimate, methods_stack)


def with_prefix(form, prefix):
    """ Return a new form with ``prefix`` added """
    word, tag, estimate, methods_stack = form
    return (prefix+word, tag, estimate, methods_stack)


def replace_methods_stack(form, new_methods_stack):
    """
    Return a new form with ``methods_stack``
    replaced with ``new_methods_stack``
    """
    return form[:3] + (new_methods_stack,)


def without_last_method(form):
    """ Return a new form without last method from methods_stack """
    stack = form[3][:-1]
    return form[:3] + (stack,)


def append_method(form, method):
    """ Return a new form with ``method`` added to methods_stack """
    stack = form[3]
    return form[:3] + (stack+(method,),)
