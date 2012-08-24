# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import os
import codecs
import collections
import string
import logging
import array

try:
    import cPickle as pickle
except ImportError:
    import pickle

import datrie
import marisa_trie

logger = logging.getLogger(__name__)

ALPHABET = '.-АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
POSSIBLE_PREFIXES = ['ПО']

DictTuple = collections.namedtuple('DictTuple', 'meta gramtab paradigms stems suffixes')

STEMS_DATA_FORMAT = str(">H")
SUFFIXES_DATA_FORMAT = str(">HH")

def _full_lemmas(filename):
    """
    Iterator over "full" lemmas in OpenCorpora dictionary file (in .txt format).
    """
    with codecs.open(filename, 'rb', 'utf8') as f:
        it = iter(f)

        while True:
            try:
                lemma = []
                line = next(it).strip()
                lemma_id = int(line)
                while line:
                    line = next(it).strip()
                    if line:
                        parts = line.split(None, 1)
                        if len(parts) == 2:
                            form, tag = parts
                        else:
                            form, tag = parts, ''
                        lemma.append((form, tag))

                yield lemma

            except StopIteration:
                break

def _to_paradigm(lemma):
    """
    Extracts (stem, paradigm) pair from lemma list.
    Paradigm is a list of suffixes with associated gram. tags. and prefixes.
    # Word beginning is marked with '.' sign.
    """
    forms, tags = list(zip(*lemma))
    prefixes = [''] * len(tags)

#    if len(forms) == 1:
#        # we put single words to suffix in order to reduce the lookup time.
#        # XXX: there should be benchmarks for this!!
#        suffix = forms[0][::-1]+'.'
#        return "", ((suffix, tags[0], ''),)

    stem = os.path.commonprefix(forms)


    if stem == "":
        for prefix in POSSIBLE_PREFIXES:
            without_prefixes = [
                form[len(prefix):] if form.startswith(prefix) else form
                for form in forms
            ]
            new_stem = os.path.commonprefix(without_prefixes)
            if new_stem:
                prefixes = [prefix if form.startswith(prefix) else '' for form in forms]
                stem = new_stem
                break

    if stem == "":
        # There is no common stem;
        # in order to reduce the lookup time for such words
        # '.' sign is moved to suffix; this way tagger won't need to
        # look at stem at all.

#        suffixes = (form[::-1]+'.' for form in forms)
        suffixes = (form[::-1] for form in forms)
        return "", tuple(zip(suffixes, tags, prefixes))


#    def pref_length(index):
#        if index is None:
#            return 0
#        return len(POSSIBLE_PREFIXES[index])

    suffixes = (
        form[len(pref)+len(stem):][::-1]
        for form, pref in zip(forms, prefixes)
    )
#    return stem[::-1] + '.', tuple(zip(suffixes, tags, prefixes))
    return stem[::-1], tuple(zip(suffixes, tags, prefixes))

def _gram_structures(filename):
    """
    Returns (gramtab, stems, paradigms, suffixes) tuple with
    compacted dictionary data.

    gramtab: ['tag1', 'tag2', ...]

    stems: Trie(
        'stem1': (para_id1, para_id2, ...),
        'stem2': (para_id1, para_id2, ...),
        ...
    )

    paradigms: [
        (
            (suffix1, tag_index1, prefix1),
            (suffix2, tag_index2, prefix2),
            ...
        ),
        (
            ...
    ]

    suffixes: Trie(
        'suffix1': (
            (para_id1, index1),
            (para_id2, index2),
            ...
        ),
        ...

#        'suffix1': {
#            'para_id1': (index1, index2, ...),
#            'para_id2': (index1, index2, ...),
#            ...
#        },
#        ...

    )
    """
    gramtab = []
    paradigms = []

    seen_tags = dict()
    seen_paradigms = dict()

#    stems_trie = datrie.Trie(ALPHABET)
#    suffixes_trie = datrie.Trie(ALPHABET)

    stems_data = set()
    suffixes_data = set()

    logger.debug("%20s %15s %15s %15s %15s", "stem", "len(gramtab)", "len(stems)", "len(paradigms)", "len(suffixes)")

    for index, lemma in enumerate(_full_lemmas(filename)):
        stem, paradigm = _to_paradigm(lemma)

        # build gramtab
        for suff, tag, pref in paradigm:
            if tag not in seen_tags:
                seen_tags[tag] = len(gramtab)
                gramtab.append(tag)

        # build paradigm index
        if paradigm not in seen_paradigms:
            seen_paradigms[paradigm] = len(paradigms)
            paradigms.append(
                tuple([(suff, seen_tags[tag], pref) for suff, tag, pref in paradigm])
            )

        para_id = seen_paradigms[paradigm]

        # build stems dict
        stems_data.add((stem, (para_id, )))

#        if stem not in stems_trie:
#            stems_trie[stem] = set()
#        stems_trie[stem].add(para_id)

        # build suffixes dict
        for idx, (suff, tag, pref) in enumerate(paradigm):
            suffixes_data.add((suff, (para_id, idx)))

#            if suff not in suffixes_trie:
#                suffixes_trie[suff] = set()
#
#            suffixes_trie[suff].add((para_id, idx))

#            suff_dct = suffixes_trie[suff]
#            if para_id not in suff_dct:
#                suff_dct[para_id] = set()
#            suff_dct[para_id].add(idx)


        if not (index % 10000):
            logger.debug("%20s %15s %15s %15s %15s",
                stem, len(gramtab), len(stems_data), len(paradigms), len(suffixes_data))

#    logger.debug('reducing memory usage..')
#    # convert sets to arrays in order to reduce memory usage
#    for key, value in stems_trie.items():
#        stems_trie[key] = tuple(sorted(list(value)))
#
#    for key, value in suffixes_trie.items():
##        for para_id in value:
##            suffixes_trie[key][para_id] = tuple(value[para_id])
#        suffixes_trie[key] = tuple(sorted(list(value)))

    logger.debug('building tries..')
    stems_trie = marisa_trie.RecordTrie(STEMS_DATA_FORMAT, stems_data, order=marisa_trie.LABEL_ORDER)
    suffixes_trie = marisa_trie.RecordTrie(SUFFIXES_DATA_FORMAT, suffixes_data, order=marisa_trie.LABEL_ORDER)

#    stems_trie_and_values = _compact_stems_trie(stems_trie)
#    suffixes_trie_and_values = _compact_suffixes_trie(suffixes_trie)
    return tuple(gramtab), stems_trie, paradigms, suffixes_trie

def _new_4byte_array():
    """
    Returns an array.array with 4+ byte unsigned integer items.
    """
    arr = array.array(str('I'))
    if arr.itemsize == 4:
        return arr
    return array.array(str('L'))


def _compact_stems_trie(trie):
    """
    Creates a read-only representation of a
    Trie where values are variable-length lists/tuples of integers.

    Returns a tuple (base_trie, values) where base_trie is a trie
    which values are indices in a ``values`` array. ``values[index]``
    is a length of original value. Original iterable can be calculated as
    ``values[index+1:index+values[index]]``.
    """

    int_trie = datrie.BaseTrie(ALPHABET)
    values = _new_4byte_array()

    state = datrie.State(trie)
    it = datrie.Iterator(state)

    while it.next():
        key, value = it.key(), it.data()
        index = len(values)
        values.append(len(value))
        values.extend(value)
        int_trie[key] = index
    return int_trie, values

def _compact_suffixes_trie(trie):
    """ Creates a read-only representation of a suffixes trie """

    int_trie = datrie.BaseTrie(ALPHABET)

    paradigm_ids = array.array(str('H'))
    paradigms_indices = array.array(str('H'))

    state = datrie.State(trie)
    it = datrie.Iterator(state)

    while it.next():
        key, value = it.key(), it.data()

        index = len(paradigm_ids)

        # FIXME: length is stored twice
        paradigm_ids.append(len(value))
        paradigms_indices.append(len(value))

        ids, indices = zip(*value)
        paradigm_ids.extend(ids)
        paradigms_indices.extend(indices)

        int_trie[key] = index
    return int_trie, (paradigm_ids, paradigms_indices)


def _get_word_parses(filename):
    word_parses = collections.defaultdict(list) # word -> possible tags

    logger.debug("%10s %20s", "lemma #", "result size")
    for index, lemma in enumerate(_full_lemmas(filename)):
        for word, tag in lemma:
            word_parses[word].append(tag)

        if not index % 10000:
            logger.debug('%10s %20s', index, len(word_parses))

    return word_parses

def _get_test_suite(word_parses, word_limit=100):
    """
    Limits word_parses to ``word_limit`` words per tag.
    """
    gramtab = collections.Counter() # tagset -> number of stored items
    result = list()
    for word in word_parses:
        parses = word_parses[word]
        gramtab.update(parses)
        if any(gramtab[tag] < word_limit for tag in parses):
            result.append((word, parses))

    return result


def _save_test_suite(path, suite):
    with open(path, 'wb') as f:
        for word, parses in suite:
            txt = "|".join([word]+parses) +'\n'
            f.write(txt.encode('utf8'))


def opencorpora_dict_to_test_suite(opencorpora_txt_path, out_path, word_limit=100):
    """
    Extracts test data from OpenCorpora .txt dictionary (at least
    ``word_limit`` words for each distinct gram. tag) and saves it to a file.
    """
    logger.debug('loading dictionary to memory...')
    parses = _get_word_parses(opencorpora_txt_path)
    logger.debug('dictionary size: %d', len(parses))

    logger.debug('building test suite...')
    suite = _get_test_suite(parses, word_limit)

    logger.debug('test suite size: %d', len(suite))

    logger.debug('saving...')
    _save_test_suite(out_path, suite)


def convert_opencorpora_dict(opencorpora_txt_path, out_path):
    """
    Converts a dictionary from OpenCorpora txt format to
    Pymorphy2 compacted internal format.
    """
    gramtab, stems_trie, paradigms, suffixes_trie = _gram_structures(opencorpora_txt_path)
    meta = {'version': 1}
    with open(out_path, 'wb', buffering=0) as f:
        pickle.dump(meta, f, 0)
        pickle.dump(gramtab, f, 2)
        pickle.dump(paradigms, f, 2)
        stems_trie.write(f)
        suffixes_trie.write(f)
#        pickle.dump(stems_values, f, 2)
#        pickle.dump(suffixes_values, f, 2)
#        stems_trie.write(f)
#        suffixes_trie.write(f)


def load_dict(path):
    """
    Loads Pymorphy2 dictionary from a file.
    """
    meta, gramtab, paradigms, stems_trie, suffixes_trie = [None]*5
    with open(path, 'rb', buffering=0) as f:
        meta = pickle.load(f)
        gramtab = pickle.load(f)
        paradigms = pickle.load(f)

        stems_trie = marisa_trie.RecordTrie(STEMS_DATA_FORMAT)
        stems_trie.read(f)

        suffixes_trie = marisa_trie.RecordTrie(SUFFIXES_DATA_FORMAT)
        suffixes_trie.read(f)

    return DictTuple(meta, gramtab, paradigms, stems_trie, suffixes_trie)
