# -*- coding: utf-8 -*-
"""
Module with utilities for converting OpenCorpora dictionaries
to pymorphy2 compact formats.
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


def _parse_opencorpora_xml(filename):
    """
    Parses OpenCorpora dict XML and returns a tuple

        (lemmas_list, links, grammemes, version, revision)

    """
    from lxml import etree

    links = []
    lemmas = {}
    grammemes = []
    version, revision = None, None

    def _clear(elem):
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]


    for ev, elem in etree.iterparse(filename):

        if elem.tag == 'grammeme':
            grammeme = elem.text
            parent = elem.get('parent')
            alias = elem.get('alias')
            grammemes.append((grammeme, parent, alias))
            _clear(elem)

        if elem.tag == 'dictionary':
            version = elem.get('version')
            revision = elem.get('revision')
            _clear(elem)

        if elem.tag == 'lemma':
            lemma_id, lemma_forms = _lemma_forms_from_xml_elem(elem)
            lemmas[lemma_id] = lemma_forms
            _clear(elem)

        elif elem.tag == 'link':
            link_tuple = (
                int(elem.get('from')),
                int(elem.get('to')),
                int(elem.get('type')),
            )
            links.append(link_tuple)
            _clear(elem)

    return lemmas, links, grammemes, version, revision

def _lemma_forms_from_xml_elem(elem):
    """
    Returns a list of (word, tags) pairs given an XML element with lemma.
    """
    def _tags(elem):
        return ",".join(g.get('v') for g in elem.findall('g'))

    lemma = []
    lemma_id = int(elem.get('id'))

    if len(elem) == 0: # deleted lemma
        return lemma_id, lemma

    base_info = elem.findall('l')

    assert len(base_info) == 1
    base_tags = _tags(base_info[0])

    for form_elem in elem.findall('f'):
        tags = _tags(form_elem)
        form = form_elem.get('t').upper()
        lemma.append(
            (form, " ".join([base_tags, tags]).strip())
        )

    return lemma_id, lemma

def _longest_common_substring(data):
    """
    Returns a longest common substring of a list of strings.
    See http://stackoverflow.com/questions/2892931/
    """
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr) and all(data[0][i:i+j] in x for x in data):
                    substr = data[0][i:i+j]
    return substr

def _to_paradigm(lemma):
    """
    Extracts (stem, paradigm) pair from lemma list.
    Paradigm is a list of suffixes with associated gram. tags and prefixes.
    """
    forms, tags = list(zip(*lemma))
    prefixes = [''] * len(tags)

    stem = os.path.commonprefix(forms)

    if stem == "":
        stem = _longest_common_substring(forms)
        prefixes = [form[:form.index(stem)] for form in forms]
        if any(pref not in LEMMA_PREFIXES for pref in prefixes):
            stem = ""
            prefixes = [''] * len(tags)

    suffixes = (
        form[len(pref)+len(stem):]
        for form, pref in zip(forms, prefixes)
    )

    return stem, tuple(zip(suffixes, tags, prefixes))


def xml_dict_to_json(xml_filename, json_filename):
    logger.info('parsing xml...')
    parsed_dct = _parse_opencorpora_xml(xml_filename)

    logger.info('writing json...')
    with codecs.open(json_filename, 'w', 'utf8') as f:
        json.dump(parsed_dct, f, ensure_ascii=False)

def _load_json_dict(filename):
    with codecs.open(filename, 'r', 'utf8') as f:
        return json.load(f)


def _join_lemmas(lemmas, links):
    """
    Combines linked lemmas to single lemma.
    """

#    <link_types>
#    <type id="1">ADJF-ADJS</type>
#    <type id="2">ADJF-COMP</type>
#    <type id="3">INFN-VERB</type>
#    <type id="4">INFN-PRTF</type>
#    <type id="5">INFN-GRND</type>
#    <type id="6">PRTF-PRTS</type>
#    <type id="7">NAME-PATR</type>
#    <type id="8">PATR_MASC-PATR_FEMN</type>
#    <type id="9">SURN_MASC-SURN_FEMN</type>
#    <type id="10">SURN_MASC-SURN_PLUR</type>
#    <type id="11">PERF-IMPF</type>
#    <type id="12">ADJF-SUPR_ejsh</type>
#    <type id="13">PATR_MASC_FORM-PATR_MASC_INFR</type>
#    <type id="14">PATR_FEMN_FORM-PATR_FEMN_INFR</type>
#    <type id="15">ADJF_eish-SUPR_nai_eish</type>
#    <type id="16">ADJF-SUPR_ajsh</type>
#    <type id="17">ADJF_aish-SUPR_nai_aish</type>
#    <type id="18">ADJF-SUPR_suppl</type>
#    <type id="19">ADJF-SUPR_nai</type>
#    <type id="20">ADJF-SUPR_slng</type>
#    </link_types>

    EXCLUDED_LINK_TYPES = set([7, ])
#    ALLOWED_LINK_TYPES = set([3, 4, 5])

    moves = dict()

    def move_lemma(from_id, to_id):
        lm = lemmas[str(from_id)]

        while to_id in moves:
            to_id = moves[to_id]

        lemmas[str(to_id)].extend(lm)
        del lm[:]
        moves[from_id] = to_id


    for link_start, link_end, type_id in links:
        if type_id in EXCLUDED_LINK_TYPES:
            continue

#        if type_id not in ALLOWED_LINK_TYPES:
#            continue

        move_lemma(link_end, link_start)

    lemma_ids = sorted(lemmas.keys(), key=int)
    return [lemmas[lemma_id] for lemma_id in lemma_ids if lemmas[lemma_id]]


def _linearized_paradigm(paradigm):
    return array.array(str("H"), list(itertools.chain(*zip(*paradigm))))

def _load_json_or_xml_dict(filename):
    if filename.endswith(".json"):
        logger.info('loading json...')
        return _load_json_dict(filename)
    else:
        logger.info('parsing xml...')
        return _parse_opencorpora_xml(filename)

def _suffixes_prediction_data(words, popularity, gramtab, paradigms,
                              min_ending_freq=2, min_paradigm_popularity=3,
                              max_forms_per_class=1):

    # XXX: this uses approach different from pymorphy 0.5.6;
    # what are the implications on prediction quality?

    productive_paradigms = set(
        para_id
        for (para_id, count) in popularity.items()
        if count >= min_paradigm_popularity
    )

    ending_counts = collections.Counter()

    endings = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))

    for word, (para_id, idx) in words:

        if para_id not in productive_paradigms:
            continue

        paradigm = paradigms[para_id]
        tag = gramtab[paradigm[len(paradigm) // 3 + idx]]
        cls = tuple(tag.replace(' ', ',', 1).split(','))[0]

        for i in 1,2,3,4,5:
            word_end = word[-i:]
            ending_counts[word_end] += 1
            endings[word_end][cls][(para_id, idx)] += 1

    counted_suffixes_dawg_data = []
    for suff in endings:

        if ending_counts[suff] < min_ending_freq:
            continue

        for cls in endings[suff]:
            for form, cnt in endings[suff][cls].most_common(max_forms_per_class):
                counted_suffixes_dawg_data.append(
                    (suff, (cnt,)+ form)
                )

    return counted_suffixes_dawg_data



def _gram_structures(lemmas, links, prediction_options=None):
    """
    Returns compacted dictionary data.
    """
    prediction_options = prediction_options or {}
    gramtab = []
    paradigms = []
    words = []

    seen_tags = dict()
    seen_paradigms = dict()

    logger.info("inlining lemma links...")
    lemmas = _join_lemmas(lemmas, links)

    logger.info('building paradigms...')
    logger.debug("%20s %15s %15s %15s", "stem", "len(gramtab)", "len(words)", "len(paradigms)")

    popularity = collections.Counter()

    for index, lemma in enumerate(lemmas):
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
        popularity[para_id] += 1

        for idx, (suff, tag, pref) in enumerate(paradigm):
            form = pref+stem+suff
            words.append(
                (form, (para_id, idx))
            )

        if not (index % 10000):
            logger.debug("%20s %15s %15s %15s", stem, len(gramtab), len(words), len(paradigms))

    logger.debug("%20s %15s %15s %15s", "total:", len(gramtab), len(words), len(paradigms))
    logger.debug("linearizing paradigms..")

    def get_form(para):
        return list(next(izip(*para)))

    forms = [get_form(para) for para in paradigms]
    suffixes = sorted(list(set(list(itertools.chain(*forms)))))
    suffixes_dict = dict(
        (suff, index)
        for index, suff in enumerate(suffixes)
    )

    def fix_strings(paradigm):
        para = []
        for suff, tag, pref in paradigm:
            para.append(
                (suffixes_dict[suff], tag, LEMMA_PREFIXES.index(pref))
            )
        return para

    paradigms = (fix_strings(para) for para in paradigms)
    paradigms = [_linearized_paradigm(paradigm) for paradigm in paradigms]

    logger.debug('calculating prediction data..')
    suffixes_dawg_data = _suffixes_prediction_data(words, popularity, gramtab, paradigms, **prediction_options)

    logger.debug('building word DAWG..')
    words_dawg = dawg.WordsDawg(words)

    del words

    logger.debug('building prediction_suffixes DAWG..')
    prediction_suffixes_dawg = dawg.PredictionSuffixesDAWG(suffixes_dawg_data)

    return tuple(gramtab), suffixes, paradigms, words_dawg, prediction_suffixes_dawg


def to_pymorphy2_format(opencorpora_dict_path, out_path, overwrite=False, prediction_options=None):
    """
    Converts a dictionary from OpenCorpora xml format to
    Pymorphy2 compacted internal format.

    ``out_path`` should be a name of folder where to put dictionaries.
    """
    dawg.assert_can_create()

    # create the output folder
    try:
        logger.debug("Creating output folder %s", out_path)
        os.mkdir(out_path)
    except OSError:
        if overwrite:
            logger.info("Output folder already exists, overwriting..")
        else:
            logger.warning("Output folder already exists!")
            return

    # load & compile dictionary
    lemmas, links, grammemes, version, revision = _load_json_or_xml_dict(opencorpora_dict_path)
    gramtab, suffixes, paradigms, words_dawg, prediction_suffixes_dawg = _gram_structures(
        lemmas, links, prediction_options=prediction_options
    )
    prediction_prefixes_dawg = dawg.DAWG(PREDICTION_PREFIXES)

    logger.info("Saving...")
    _f = lambda path: os.path.join(out_path, path)

    with codecs.open(_f('grammemes.json'), 'w', 'utf8') as f:
        json.dump(grammemes, f, ensure_ascii=False)

    gramtab_formats = {}
    for format, Tag in tagset.registry.items():
        Tag._init_restrictions(grammemes)
        new_gramtab = [Tag._from_internal_tag(tag) for tag in gramtab]

        gramtab_name = "gramtab-%s.json" % format
        gramtab_formats[format] = gramtab_name

        with codecs.open(_f(gramtab_name), 'w', 'utf8') as f:
            json.dump(new_gramtab, f, ensure_ascii=False)


    with codecs.open(_f('suffixes.json'), 'w', 'utf8') as f:
        json.dump(suffixes, f, ensure_ascii=False)

    with open(_f('paradigms.array'), 'wb') as f:
        f.write(struct.pack(str("<H"), len(paradigms)))
        for para in paradigms:
            f.write(struct.pack(str("<H"), len(para)))
            para.tofile(f)

    words_dawg.save(_f('words.dawg'))
    prediction_suffixes_dawg.save(_f('prediction-suffixes.dawg'))
    prediction_prefixes_dawg.save(_f('prediction-prefixes.dawg'))

    logger.debug("computing metadata..")

    def _dawg_len(dawg):
        return sum(1 for k in dawg.iterkeys())

    logger.debug('  words_dawg_len')
    words_dawg_len = _dawg_len(words_dawg)
    logger.debug('  prediction_suffixes_dawg_len')
    prediction_suffixes_dawg_len = _dawg_len(prediction_suffixes_dawg)

    meta = [
        ['format_version', 1],
        ['pymorphy2_version', pymorphy2.__version__],
        ['compiled_at', datetime.datetime.utcnow().isoformat()],

        ['source', 'opencorpora.org'],
        ['source_version', version],
        ['source_revision', revision],
        ['source_lemmas_count', len(lemmas)],
        ['source_links_count', len(links)],

        ['gramtab_length', len(gramtab)],
        ['gramtab_formats', gramtab_formats],
        ['paradigms_length', len(paradigms)],
        ['suffixes_length', len(suffixes)],

        ['words_dawg_length', words_dawg_len],
        ['prediction_suffixes_dawg_length', prediction_suffixes_dawg_len],
        ['prediction_prefixes_dawg_length', len(PREDICTION_PREFIXES)],
    ]

    with codecs.open(_f('meta.json'), 'w', 'utf8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=4)



DictTuple = collections.namedtuple('DictTuple', 'meta gramtab suffixes paradigms words prediction_prefixes prediction_suffixes Tag')

def load(path, gramtab_format='opencorpora-int'):
    """
    Loads Pymorphy2 dictionary.
    ``path`` is a folder name where dictionary data reside.
    """
    #meta, gramtab, suffixes, paradigms, words = [None]*5

    _f = lambda p: os.path.join(path, p)

    with open(_f('meta.json'), 'r') as f:
        meta = json.load(f)
        if hasattr(collections, 'OrderedDict'):
            meta = collections.OrderedDict(meta)
        else:
            meta = dict(meta)

    format_version = meta.get('format_version', None)
    if format_version != 1:
        raise ValueError("This dictionary format ('%s') is not supported." % format_version)

    if gramtab_format not in tagset.registry:
        raise ValueError("This gramtab format ('%s') is unsupported." % gramtab_format)
    Tag = tagset.registry[gramtab_format]

    with open(_f('grammemes.json'), 'r') as f:
        grammemes = json.load(f, encoding='utf8')
        Tag._init_restrictions(grammemes)


    gramtab_formats = meta.get('gramtab_formats', {})
    if gramtab_format not in gramtab_formats:
        raise ValueError("This gramtab format (%s) is unavailable; available formats: %s" % (gramtab_format, gramtab_formats.keys()))

    with open(_f(gramtab_formats[gramtab_format]), 'r') as f:
        gramtab = [Tag(tag_str) for tag_str in json.load(f, encoding='utf8')]

    with open(_f('suffixes.json'), 'r') as f:
        suffixes = json.load(f)

    paradigms = []
    with open(_f('paradigms.array'), 'rb') as f:
        paradigms_count = struct.unpack(str("<H"), f.read(2))[0]

        for x in range(paradigms_count):
            paradigm_len = struct.unpack(str("<H"), f.read(2))[0]
            para = array.array(str("H"))
            para.fromfile(f, paradigm_len)
            paradigms.append(para)

    words = dawg.WordsDawg().load(_f('words.dawg'))
    prediction_suffixes = dawg.PredictionSuffixesDAWG().load(_f('prediction-suffixes.dawg'))
    prediction_prefixes = dawg.DAWG().load(_f('prediction-prefixes.dawg'))
    return DictTuple(meta, gramtab, suffixes, paradigms, words, prediction_prefixes, prediction_suffixes, Tag)
