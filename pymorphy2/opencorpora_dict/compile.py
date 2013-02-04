# -*- coding: utf-8 -*-
"""
Module for converting OpenCorpora dictionaries
to pymorphy2 representation.
"""
from __future__ import absolute_import, unicode_literals
import os
import logging
import collections
import itertools
import array

try:
    izip = itertools.izip
except AttributeError:
    izip = zip

from pymorphy2 import dawg
from pymorphy2.constants import LEMMA_PREFIXES, PREDICTION_PREFIXES
from pymorphy2.utils import longest_common_substring

logger = logging.getLogger(__name__)


CompiledDictionary = collections.namedtuple(
    'CompiledDictionary',
    'gramtab suffixes paradigms words_dawg prediction_suffixes_dawg parsed_dict'
)


def convert_to_pymorphy2(opencorpora_dict_path, out_path, overwrite=False,
                         prediction_options=None):
    """
    Convert a dictionary from OpenCorpora XML format to
    Pymorphy2 compacted format.

    ``out_path`` should be a name of folder where to put dictionaries.
    """
    from .parse import load_json_or_xml_dict
    from .storage import save_compiled_dict

    dawg.assert_can_create()
    if not _create_out_path(out_path, overwrite):
        return

    parsed_dict = load_json_or_xml_dict(opencorpora_dict_path)
    compiled_dict = compile_parsed_dict(parsed_dict, prediction_options)

    save_compiled_dict(compiled_dict, out_path)


def compile_parsed_dict(parsed_dict, prediction_options=None):
    """
    Return compacted dictionary data.
    """
    prediction_options = prediction_options or {}
    gramtab = []
    paradigms = []
    words = []

    seen_tags = dict()
    seen_paradigms = dict()

    logger.info("inlining lemma links...")
    lemmas = _join_lemmas(parsed_dict.lemmas, parsed_dict.links)

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
        """ Replace suffix and prefix with the respective id numbers. """
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

    return CompiledDictionary(tuple(gramtab), suffixes, paradigms,
                              words_dawg, prediction_suffixes_dawg, parsed_dict)


def _join_lemmas(lemmas, links):
    """
    Combine linked lemmas to single lemma.
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


def _to_paradigm(lemma):
    """
    Extract (stem, paradigm) pair from lemma (which is a list of
    (word_form, tag) tuples). Paradigm is a list of suffixes with
    associated tags and prefixes.
    """
    forms, tags = list(zip(*lemma))
    prefixes = [''] * len(tags)

    if len(forms) == 1:
        stem = forms[0]
    else:
        stem = longest_common_substring(forms)
        prefixes = [form[:form.index(stem)] for form in forms]

        # only allow prefixes from LEMMA_PREFIXES
        if any(pref not in LEMMA_PREFIXES for pref in prefixes):
            stem = ""
            prefixes = [''] * len(tags)

    suffixes = (
        form[len(pref)+len(stem):]
        for form, pref in zip(forms, prefixes)
    )

    return stem, tuple(zip(suffixes, tags, prefixes))


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


def _linearized_paradigm(paradigm):
    """
    Convert ``paradigm`` (a list of tuples with numbers)
    to 1-dimensional array.array (for reduced memory usage).
    """
    return array.array(str("H"), list(itertools.chain(*zip(*paradigm))))


def _create_out_path(out_path, overwrite=False):
    try:
        logger.debug("Creating output folder %s", out_path)
        os.mkdir(out_path)
    except OSError:
        if overwrite:
            logger.info("Output folder already exists, overwriting..")
        else:
            logger.warning("Output folder already exists!")
            return False
    return True

