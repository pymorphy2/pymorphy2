# -*- coding: utf-8 -*-
# cython: profile=True
from __future__ import print_function, unicode_literals
import math
import bisect
import time

import pymorphy2.data


def merge_intersect(pref_paradigms, suff_paradigms_ids, suff_indices):
    """
    Merge-style intersection of 2 sorted tuples. Items in pref_paradigms
    must be unique; items in suff_paradigms may have duplicate paradigms.
    """
    suff_idx = 0
    pref_idx = 0
    res = []

    suff_para_len = len(suff_paradigms_ids)
    pref_para_len =  len(pref_paradigms)

    while suff_idx < suff_para_len and pref_idx < pref_para_len:
        para_id = suff_paradigms_ids[suff_idx]
        prefix_para_id = pref_paradigms[pref_idx]

        if para_id == prefix_para_id:
            info_idx = suff_indices[suff_idx]
            res.append((para_id, info_idx))
            suff_idx += 1
            #pref_idx += 1
        elif para_id > prefix_para_id:
            pref_idx += 1
        else:
            suff_idx += 1

    return res


def bisect_intersect(pref_paradigms, suff_data):
    """
    Intersection of 2 sorted tuples; binary search is used for
    items from pref_paradigms.

    Items in pref_paradigms must be unique; items in suff_paradigms may
    have duplicate paradigms.
    """
    i = 0
    res = []
    for para_id, info_idx in suff_data:
        i = bisect.bisect_left(pref_paradigms, para_id, lo=i)
        if i >= len(pref_paradigms):
            break

        if pref_paradigms[i] == para_id:
            res.append((para_id, info_idx))

    return res


def bisect_intersect2(pref_paradigms, suff_data):
    """
    Intersection of 2 sorted tuples; binary search is used for
    items from suff_paradigms.

    Items in pref_paradigms must be unique; items in suff_paradigms may
    have duplicate paradigms.
    """
    i = 0
    res = []
    suff_paradigms_len = len(suff_data)

    for prefix_para_id in pref_paradigms:
        base = prefix_para_id, 0

        #i = bisect.bisect_left(suff_paradigms_ids, prefix_para_id, lo=i)
        i = bisect.bisect_left(suff_data, base, lo=i)
        if i >= suff_paradigms_len:
            break

        para_id, info_idx = suff_data[i]
        #para_id = suff_paradigms_ids[i]
        while prefix_para_id == para_id:
            #info_idx = suff_indices[i]
            res.append((para_id, info_idx))
            i += 1
            if i >= suff_paradigms_len:
                break
            #para_id = suff_paradigms_ids[i]
            #info_idx = suff_indices[i]
            para_id, info_idx = suff_data[i]

    return res

def get_prefix_paradigms(dictionary, inversed_prefix):
    return [p[0] for p in dictionary.stems[inversed_prefix]]

def get_suffix_paradigms(dictionary, suff):
    suff_data = dictionary.suffixes[suff]
    return suff_data
    #return list(zip(*suff_data))

#    _idx = dictionary.suffixes[suff]
#    para_ids, indices = dictionary.suffixes_values
#    start, end = _idx+1, _idx+para_ids[_idx]+1
#    return para_ids[start:end], indices[start:end]


def tag(dictionary, word, form_prefix=''):
    inversed_word = word[::-1] # +'.'
    possible_suffixes = dictionary.suffixes.prefixes(inversed_word)[::-1] + ['']

#    cdef pref_paradigms
#    cdef dict suff_paradigms
#    cdef int suff_idx, pref_idx

#    cdef unicode prefix
#    cdef set common_paradigms
#    cdef list res
#    cdef int para_id, info_idx, graminfo_id
#    cdef unicode graminfo

    result = []
    for suff in possible_suffixes:
        inversed_prefix = inversed_word[len(suff):]
        if inversed_prefix in dictionary.stems:

#            pref_para = dictionary.stems[inversed_prefix]
#            suff_para = dictionary.suffixes(suff)

            pref_paradigms = get_prefix_paradigms(dictionary, inversed_prefix)
            suff_paradigms = get_suffix_paradigms(dictionary, suff)

            # We can use python sets but they require much more memory.
            # So the intersection works on 2 sorted tuples.
            # For near-equal tuples merge-style intersection is efficient;
            # when one of tuples is much greater than an another,
            # binary search is better.

            L1, L2 = len(suff_paradigms), len(pref_paradigms)
#            merge_estimation = L1 + L2
#            bisect_estimation = L1 * (1 + math.log(L2+1, 2))
#            bisect_estimation2 = L2 * (1 + math.log(L1+1, 2))

#            print(merge_estimation, bisect_estimation, bisect_estimation2, L1, L2)
#
#            for meth in merge_intersect, bisect_intersect, bisect_intersect2:
#                start = time.time()
#                for x in range(1000):
#                    meth(pref_paradigms, suff_paradigms_ids, suff_indices)
#                print(meth, time.time()-start)

#            if (merge_estimation < bisect_estimation and merge_estimation < bisect_estimation2):
#                res = merge_intersect(pref_paradigms, suff_paradigms_ids, suff_indices)
#            elif (bisect_estimation < bisect_estimation2):
            if (L1 < L2):
                res = bisect_intersect(pref_paradigms, suff_paradigms)
            else:
                res = bisect_intersect2(pref_paradigms, suff_paradigms)

            if res:
                # remove forms that don't have a required prefix
                for para_id, info_idx in res:
                    info = dictionary.paradigms[para_id][info_idx]

                    if form_prefix == info[2]:
                        gram_tag = dictionary.gramtab[info[1]]
                        result.append(gram_tag)

    if not form_prefix:
        # try to parse the word as prefixed
        for prefix in pymorphy2.data.POSSIBLE_PREFIXES:
            if word.startswith(prefix):
                res = tag(dictionary, word[len(prefix):], prefix)
                result.extend(res)

    return result

#def normal_forms(dictionary, word):
#    word = word[::-1]
#    possible_suffixes = dictionary.suffixes.prefix_items(word)[::-1] # longest first
#
#    for suff, suff_paradigms in possible_suffixes:
#        prefix = word[len(suff):]
#
#        if prefix in dictionary.stems:
#            res = []
#            seen = set()
#
#            pref_paradigms = set(dictionary.stems[prefix])
#            for para_id, info_idx in suff_paradigms:
#                if para_id in pref_paradigms:
#                    norm_suffix = dictionary.paradigms[para_id][0][0]
#                    if norm_suffix not in seen:
#                        seen.add(norm_suffix)
#                        res.append("".join([norm_suffix, prefix])[::-1])
#            if res:
#                return res
