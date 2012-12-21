# -*- coding: utf-8 -*-
"""
Module for saving and loading pymorphy2 dictionaries.
"""
from __future__ import absolute_import, unicode_literals
import datetime
import codecs
import os
import logging
import collections
import json
import itertools
import array
import struct

try:
    izip = itertools.izip
except AttributeError:
    izip = zip

import pymorphy2
from pymorphy2 import tagset
from pymorphy2 import dawg
from pymorphy2.constants import LEMMA_PREFIXES, PREDICTION_PREFIXES

logger = logging.getLogger(__name__)


LoadedDictionary = collections.namedtuple(
    'LoadedDictionary',
    'meta gramtab suffixes paradigms words prediction_prefixes prediction_suffixes Tag'
)

def load_dict(path, gramtab_format='opencorpora-int'):
    """
    Load pymorphy2 dictionary.
    ``path`` is a folder name with dictionary data.
    """

    _f = lambda p: os.path.join(path, p)

    meta = _load_meta(_f('meta.json'))
    _assert_format_is_compatible(meta)

    Tag = _load_tag_class(gramtab_format, _f('grammemes.json'))
    gramtab = [Tag(tag_str) for tag_str in _load_gramtab(meta, gramtab_format, path)]

    suffixes = _load_suffixes(_f('suffixes.json'))
    paradigms = _load_paradigms(_f('paradigms.array'))
    words = dawg.WordsDawg().load(_f('words.dawg'))

    prediction_suffixes = dawg.PredictionSuffixesDAWG().load(_f('prediction-suffixes.dawg'))
    prediction_prefixes = dawg.DAWG().load(_f('prediction-prefixes.dawg'))

    return LoadedDictionary(meta, gramtab, suffixes, paradigms, words,
                            prediction_prefixes, prediction_suffixes, Tag)


def save_compiled_dict(compiled_dict, out_path):
    """
    Save a compiled_dict to ``out_path``
    ``out_path`` should be a name of folder where to put dictionaries.
    """
    logger.info("Saving...")
    _f = lambda path: os.path.join(out_path, path)

    with codecs.open(_f('grammemes.json'), 'w', 'utf8') as f:
        json.dump(compiled_dict.parsed_dict.grammemes, f, ensure_ascii=False)

    gramtab_formats = {}
    for format, Tag in tagset.registry.items():
        Tag._init_restrictions(compiled_dict.parsed_dict.grammemes)
        new_gramtab = [Tag._from_internal_tag(tag) for tag in compiled_dict.gramtab]

        gramtab_name = "gramtab-%s.json" % format
        gramtab_formats[format] = gramtab_name

        with codecs.open(_f(gramtab_name), 'w', 'utf8') as f:
            json.dump(new_gramtab, f, ensure_ascii=False)


    with codecs.open(_f('suffixes.json'), 'w', 'utf8') as f:
        json.dump(compiled_dict.suffixes, f, ensure_ascii=False)

    with open(_f('paradigms.array'), 'wb') as f:
        f.write(struct.pack(str("<H"), len(compiled_dict.paradigms)))
        for para in compiled_dict.paradigms:
            f.write(struct.pack(str("<H"), len(para)))
            para.tofile(f)

    compiled_dict.words_dawg.save(_f('words.dawg'))
    compiled_dict.prediction_suffixes_dawg.save(_f('prediction-suffixes.dawg'))

    dawg.DAWG(PREDICTION_PREFIXES).save(_f('prediction-prefixes.dawg'))

    logger.debug("computing metadata..")

    def _dawg_len(dawg):
        return sum(1 for k in dawg.iterkeys())

    logger.debug('  words_dawg_len')
    words_dawg_len = _dawg_len(compiled_dict.words_dawg)
    logger.debug('  prediction_suffixes_dawg_len')
    prediction_suffixes_dawg_len = _dawg_len(compiled_dict.prediction_suffixes_dawg)

    meta = [
        ['format_version', 1],
        ['pymorphy2_version', pymorphy2.__version__],
        ['compiled_at', datetime.datetime.utcnow().isoformat()],

        ['source', 'opencorpora.org'],
        ['source_version', compiled_dict.parsed_dict.version],
        ['source_revision', compiled_dict.parsed_dict.revision],
        ['source_lemmas_count', len(compiled_dict.parsed_dict.lemmas)],
        ['source_links_count', len(compiled_dict.parsed_dict.links)],

        ['gramtab_length', len(compiled_dict.gramtab)],
        ['gramtab_formats', gramtab_formats],
        ['paradigms_length', len(compiled_dict.paradigms)],
        ['suffixes_length', len(compiled_dict.suffixes)],

        ['words_dawg_length', words_dawg_len],
        ['prediction_suffixes_dawg_length', prediction_suffixes_dawg_len],
        ['prediction_prefixes_dawg_length', len(PREDICTION_PREFIXES)],
    ]

    with codecs.open(_f('meta.json'), 'w', 'utf8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=4)



def _load_meta(filename):
    """ Load metadata. """
    with open(filename, 'r') as f:
        meta = json.load(f)
        if hasattr(collections, 'OrderedDict'):
            return collections.OrderedDict(meta)
        return dict(meta)


def _load_tag_class(gramtab_format, grammemes_filename):
    """ Load and initialize Tag class (according to ``gramtab_format``). """
    if gramtab_format not in tagset.registry:
        raise ValueError("This gramtab format ('%s') is unsupported." % gramtab_format)

    Tag = tagset.registry[gramtab_format]

    with open(grammemes_filename, 'r') as f:
        grammemes = json.load(f, encoding='utf8')
        Tag._init_restrictions(grammemes)

    return Tag


def _load_gramtab(meta, gramtab_format, path):
    """ Load gramtab (a list of tags) """

    gramtab_formats = meta.get('gramtab_formats', {})
    if gramtab_format not in gramtab_formats:
        raise ValueError("This gramtab format (%s) is unavailable; available formats: %s" % (gramtab_format, gramtab_formats.keys()))

    gramtab_filename = os.path.join(path, gramtab_formats[gramtab_format])
    with open(gramtab_filename, 'r') as f:
        return json.load(f, encoding='utf8')


def _load_suffixes(filename):
    """ Load a list of possible word suffixes """
    with open(filename, 'r') as f:
        return json.load(f)


def _load_paradigms(filename):
    """ Load paradigms data """
    paradigms = []
    with open(filename, 'rb') as f:
        paradigms_count = struct.unpack(str("<H"), f.read(2))[0]

        for x in range(paradigms_count):
            paradigm_len = struct.unpack(str("<H"), f.read(2))[0]

            para = array.array(str("H"))
            para.fromfile(f, paradigm_len)

            paradigms.append(para)
    return paradigms


def _assert_format_is_compatible(meta):
    """ Raise an exception if dictionary format is not compatible """
    format_version = meta.get('format_version', None)
    if format_version != 1:
        raise ValueError("This dictionary format ('%s') is not supported." % format_version)

