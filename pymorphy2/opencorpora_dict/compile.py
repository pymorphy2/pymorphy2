# -*- coding: utf-8 -*-
"""
:mod:`pymorphy2.opencorpora_dict.compile` is a
module for converting OpenCorpora dictionaries
to pymorphy2 representation.
"""
from __future__ import absolute_import, unicode_literals
import os
import logging
import collections
import itertools
import array
import operator

try:
    izip = itertools.izip
except AttributeError:
    izip = zip

from pymorphy2 import dawg
from pymorphy2.constants import PARADIGM_PREFIXES, PREDICTION_PREFIXES
from pymorphy2.utils import longest_common_substring, largest_group

logger = logging.getLogger(__name__)


CompiledDictionary = collections.namedtuple(
    'CompiledDictionary',
    'gramtab suffixes paradigms words_dawg prediction_suffixes_dawgs parsed_dict prediction_options'
)


def convert_to_pymorphy2(opencorpora_dict_path, out_path, overwrite=False,
                         prediction_options=None):
    """
    Convert a dictionary from OpenCorpora XML format to
    Pymorphy2 compacted format.

    ``out_path`` should be a name of folder where to put dictionaries.
    """
    from .parse import parse_opencorpora_xml
    from .preprocess import simplify_tags
    from .storage import save_compiled_dict

    dawg.assert_can_create()
    if not _create_out_path(out_path, overwrite):
        return

    parsed_dict = parse_opencorpora_xml(opencorpora_dict_path)
    simplify_tags(parsed_dict)
    compiled_dict = compile_parsed_dict(parsed_dict, prediction_options)
    save_compiled_dict(compiled_dict, out_path)


def compile_parsed_dict(parsed_dict, prediction_options=None):
    """
    Return compacted dictionary data.
    """
    _prediction_options = dict(
        # defaults
        min_ending_freq=2,
        min_paradigm_popularity=3,
        max_suffix_length=5
    )
    _prediction_options.update(prediction_options or {})

    gramtab = []
    paradigms = []
    words = []

    seen_tags = dict()
    seen_paradigms = dict()

    logger.info("inlining lexeme derivational rules...")
    lexemes = _join_lexemes(parsed_dict.lexemes, parsed_dict.links)

    logger.info('building paradigms...')
    logger.debug("%20s %15s %15s %15s", "word", "len(gramtab)", "len(words)", "len(paradigms)")

    paradigm_popularity = collections.defaultdict(int)

    for index, lexeme in enumerate(lexemes):
        stem, paradigm = _to_paradigm(lexeme)

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
        paradigm_popularity[para_id] += 1

        for idx, (suff, tag, pref) in enumerate(paradigm):
            form = pref+stem+suff
            words.append(
                (form, (para_id, idx))
            )

        if not (index % 10000):
            word = paradigm[0][2] + stem + paradigm[0][0]
            logger.debug("%20s %15s %15s %15s", word, len(gramtab), len(words), len(paradigms))


    logger.debug("%20s %15s %15s %15s", "total:", len(gramtab), len(words), len(paradigms))
    logger.debug("linearizing paradigms..")

    def get_form(para):
        return list(next(izip(*para)))

    forms = [get_form(para) for para in paradigms]
    suffixes = sorted(set(list(itertools.chain(*forms))))
    suffixes_dict = dict(
        (suff, index)
        for index, suff in enumerate(suffixes)
    )

    def fix_strings(paradigm):
        """ Replace suffix and prefix with the respective id numbers. """
        para = []
        for suff, tag, pref in paradigm:
            para.append(
                (suffixes_dict[suff], tag, PARADIGM_PREFIXES.index(pref))
            )
        return para

    paradigms = (fix_strings(para) for para in paradigms)
    paradigms = [_linearized_paradigm(paradigm) for paradigm in paradigms]

    logger.debug('calculating prediction data..')
    suffixes_dawgs_data = _suffixes_prediction_data(
        words, paradigm_popularity, gramtab, paradigms, suffixes, **_prediction_options
    )

    logger.debug('building word DAWG..')
    words_dawg = dawg.WordsDawg(words)

    del words

    prediction_suffixes_dawgs = []
    for prefix_id, dawg_data in enumerate(suffixes_dawgs_data):
        logger.debug('building prediction_suffixes DAWGs #%d..' % prefix_id)
        prediction_suffixes_dawgs.append(dawg.PredictionSuffixesDAWG(dawg_data))

    return CompiledDictionary(tuple(gramtab), suffixes, paradigms,
                              words_dawg, prediction_suffixes_dawgs,
                              parsed_dict, _prediction_options)


def _join_lexemes(lexemes, links):
    """
    Combine linked lexemes to a single lexeme.
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

    def move_lexeme(from_id, to_id):
        lm = lexemes[str(from_id)]

        while to_id in moves:
            to_id = moves[to_id]

        lexemes[str(to_id)].extend(lm)
        del lm[:]
        moves[from_id] = to_id

    for link_start, link_end, type_id in links:
        if type_id in EXCLUDED_LINK_TYPES:
            continue

#        if type_id not in ALLOWED_LINK_TYPES:
#            continue

        move_lexeme(link_end, link_start)

    lex_ids = sorted(lexemes.keys(), key=int)
    return [lexemes[lex_id] for lex_id in lex_ids if lexemes[lex_id]]


def _to_paradigm(lexeme):
    """
    Extract (stem, paradigm) pair from lexeme (which is a list of
    (word_form, tag) tuples). Paradigm is a list of suffixes with
    associated tags and prefixes.
    """
    forms, tags = list(zip(*lexeme))
    prefixes = [''] * len(tags)

    if len(forms) == 1:
        stem = forms[0]
    else:
        stem = longest_common_substring(forms)
        prefixes = [form[:form.index(stem)] for form in forms]

        # only allow prefixes from PARADIGM_PREFIXES
        if any(pref not in PARADIGM_PREFIXES for pref in prefixes):
            stem = ""
            prefixes = [''] * len(tags)

    suffixes = (
        form[len(pref)+len(stem):]
        for form, pref in zip(forms, prefixes)
    )

    return stem, tuple(zip(suffixes, tags, prefixes))


def _suffixes_prediction_data(words, paradigm_popularity, gramtab, paradigms, suffixes,
                              min_ending_freq, min_paradigm_popularity, max_suffix_length):

    logger.debug('calculating prediction data: removing non-productive paradigms..')
    productive_paradigms = set(
        para_id
        for (para_id, count) in paradigm_popularity.items()
        if count >= min_paradigm_popularity
    )

    # ["suffix"] => number of occurrences
    # this is for removing non-productive suffixes
    ending_counts = collections.defaultdict(int)

    # [form_prefix_id]["suffix"]["POS"][(para_id, idx)] => number or occurrences
    # this is for selecting most popular parses
    endings = {}
    for form_prefix_id in range(len(PARADIGM_PREFIXES)):
        endings[form_prefix_id] = collections.defaultdict(
                                    lambda: collections.defaultdict(
                                        lambda: collections.defaultdict(int)))

    logger.debug('calculating prediction data: checking word endings..')
    for word, (para_id, idx) in words:

        if para_id not in productive_paradigms:
            continue

        paradigm = paradigms[para_id]

        form_count = len(paradigm) // 3

        tag = gramtab[paradigm[form_count + idx]]
        form_prefix_id = paradigm[2*form_count + idx]
        form_prefix = PARADIGM_PREFIXES[form_prefix_id]
        form_suffix = suffixes[paradigm[idx]]

        assert len(word) >= len(form_prefix+form_suffix), word
        assert word.startswith(form_prefix), word
        assert word.endswith(form_suffix), word

        if len(word) == len(form_prefix) + len(form_suffix):
            # pseudo-paradigms are useless for prediction
            continue

        POS = tuple(tag.replace(' ', ',', 1).split(','))[0]

        for i in range(max(len(form_suffix), 1), max_suffix_length+1): #was: 1,2,3,4,5
            word_end = word[-i:]

            ending_counts[word_end] += 1
            endings[form_prefix_id][word_end][POS][(para_id, idx)] += 1

    dawgs_data = []

    for form_prefix_id in sorted(endings.keys()):
        logger.debug('calculating prediction data: preparing DAWGs data #%d..' % form_prefix_id)
        counted_suffixes_dawg_data = []
        endings_with_prefix = endings[form_prefix_id]

        for suff in endings_with_prefix:
            if ending_counts[suff] < min_ending_freq:
                continue

            for POS in endings_with_prefix[suff]:

                common_endings = largest_group(
                    endings_with_prefix[suff][POS].items(),
                    operator.itemgetter(1)
                )

                for form, cnt in common_endings:
                    counted_suffixes_dawg_data.append(
                        (suff, (cnt,) + form)
                    )

        dawgs_data.append(counted_suffixes_dawg_data)

    return dawgs_data


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

