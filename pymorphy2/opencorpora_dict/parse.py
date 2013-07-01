# -*- coding: utf-8 -*-
"""
:mod:`pymorphy2.opencorpora_dict.parse` is a
module for OpenCorpora XML dictionaries parsing.
"""
from __future__ import absolute_import, unicode_literals, division

import logging
import collections

try:
    from lxml.etree import iterparse

    def xml_clear_elem(elem):
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

except ImportError:
    try:
        from xml.etree.cElementTree import iterparse
    except ImportError:
        from xml.etree.ElementTree import iterparse

    def xml_clear_elem(elem):
        elem.clear()


logger = logging.getLogger(__name__)

ParsedDictionary = collections.namedtuple('ParsedDictionary', 'lexemes links grammemes version revision')


def parse_opencorpora_xml(filename):
    """
    Parse OpenCorpora dict XML and return a ``ParsedDictionary`` namedtuple.
    """

    links = []
    lexemes = {}
    grammemes = []
    version, revision = None, None
    _lexemes_len = 0

    for ev, elem in iterparse(filename, events=(str('start'), str('end'))):

        if ev == 'start':
            if elem.tag == 'dictionary':
                version = elem.get('version')
                revision = elem.get('revision')
                logger.info("dictionary v%s, rev%s", version, revision)
                xml_clear_elem(elem)
            continue

        if elem.tag == 'grammeme':
            name = elem.find('name').text
            parent = elem.get('parent')
            alias = elem.find('alias').text
            description = elem.find('description').text

            grammeme = (name, parent, alias, description)
            grammemes.append(grammeme)
            xml_clear_elem(elem)

        if elem.tag == 'lemma':
            if not lexemes:
                logger.info('parsing xml:lemmas...')

            lex_id, word_forms = _word_forms_from_xml_elem(elem)
            lexemes[lex_id] = word_forms
            xml_clear_elem(elem)

        elif elem.tag == 'link':
            if not links:
                logger.info('parsing xml:links...')

            link_tuple = (
                elem.get('from'),
                elem.get('to'),
                elem.get('type'),
            )
            links.append(link_tuple)
            xml_clear_elem(elem)

        if len(lexemes) != _lexemes_len and not (len(lexemes) % 50000):
            logger.debug("%d lexemes parsed" % len(lexemes))
            _lexemes_len = len(lexemes)

    return ParsedDictionary(lexemes, links, grammemes, version, revision)


def _grammemes_from_elem(elem):
    return ",".join(g.get('v') for g in elem.findall('g'))


def _word_forms_from_xml_elem(elem):
    """
    Return a list of (word, tag) pairs given "lemma" XML element.
    """
    lexeme = []
    lex_id = elem.get('id')

    if len(elem) == 0:  # deleted lexeme?
        return lex_id, lexeme

    base_info = elem.findall('l')

    assert len(base_info) == 1
    base_grammemes = _grammemes_from_elem(base_info[0])

    for form_elem in elem.findall('f'):
        grammemes = _grammemes_from_elem(form_elem)
        form = form_elem.get('t').lower()
        lexeme.append(
            (form, " ".join([base_grammemes, grammemes]).strip())
        )

    return lex_id, lexeme
