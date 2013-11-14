# -*- coding: utf-8 -*-
"""
Module for estimating P(t|w) from partially annotated OpenCorpora XML dump
and saving this information to a file.

This module requires NLTK3 master, opencorpora-tools>=0.4.4 and dawg >= 0.7
packages for probability estimation and resulting file creation.
"""
from __future__ import absolute_import
from pymorphy2.opencorpora_dict.preprocess import tag2grammemes
from pymorphy2.dawg import ConditionalProbDistDAWG


def estimate_conditional_tag_probability(morph, corpus_filename):
    """
    Estimate P(t|w) based on OpenCorpora xml dump.

    Probability is estimated based on counts of disambiguated
    ambiguous words, using simple Laplace smoothing.
    """
    import nltk
    import opencorpora

    class _ConditionalProbDist(nltk.ConditionalProbDist):
        """
        This ConditionalProbDist subclass passes 'condition' variable to
        probdist_factory. See https://github.com/nltk/nltk/issues/500
        """
        def __init__(self, cfdist, probdist_factory):
            self._probdist_factory = probdist_factory
            for condition in cfdist:
                self[condition] = probdist_factory(cfdist[condition], condition)

    reader = opencorpora.CorpusReader(corpus_filename)

    ambiguous_words = (
        (w.lower(), tag2grammemes(t))
        for (w, t) in _disambiguated_words(reader)
        if len(morph.tag(w)) > 1
    )
    ambiguous_words = ((w, gr) for (w, gr) in ambiguous_words
                       if gr != set(['UNKN']))

    def probdist_factory(fd, condition):
        bins = max(len(morph.tag(condition)), fd.B())
        return nltk.LaplaceProbDist(fd, bins=bins)

    cfd = nltk.ConditionalFreqDist(ambiguous_words)
    cpd = _ConditionalProbDist(cfd, probdist_factory)
    return cpd, cfd


def build_cpd_dawg(morph, cpd, min_frequency):
    """
    Return conditional tag probability information encoded as DAWG.

    For each "interesting" word and tag the resulting DAWG
    stores ``"word:tag"`` key with ``probability*1000000`` integer value.
    """
    words = [word for (word, fd) in cpd.items()
             if fd.freqdist().N() >= min_frequency]

    prob_data = filter(
        lambda rec: not _all_the_same(rec[1]),
        ((word, _tag_probabilities(morph, word, cpd)) for word in words)
    )
    dawg_data = (
        ((word, tag), prob)
        for word, probs in prob_data
        for tag, prob in probs.items()
    )
    return ConditionalProbDistDAWG(dawg_data)


def _disambiguated_words(reader):
    return (
        (word, parses[0][1])
        for (word, parses) in reader.iter_parsed_words()
        if len(parses) == 1
    )


def _all_the_same(probs):
    return len(set(probs.values())) <= 1


def _parse_probabilities(morph, word, cpd):
    """
    Return probabilities of word parses
    according to CustomConditionalProbDist ``cpd``.
    """
    parses = morph.parse(word)
    probabilities = [cpd[word].prob(p.tag.grammemes) for p in parses]
    return list(zip(parses, probabilities))


def _tag_probabilities(morph, word, cpd):
    return dict(
        (p.tag, prob)
        for (p, prob) in _parse_probabilities(morph, word, cpd)
    )


