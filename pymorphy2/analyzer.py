# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import os
import heapq
import collections
import logging

from pymorphy2 import opencorpora_dict
from pymorphy2 import units

logger = logging.getLogger(__name__)

_Parse = collections.namedtuple('Parse', 'word, tag, normal_form, estimate, methods_stack')

class Parse(_Parse):
    """
    Parse result wrapper.
    """

    _morph = None
    """ :type _morph: MorphAnalyzer """

    _dict = None
    """ :type _dict: pymorphy2.opencorpora_dict.Dictionary """

    def inflect(self, required_grammemes):
        res = self._morph._inflect(self, required_grammemes)
        return None if not res else res[0]

    def make_agree_with_number(self, num):
        """
        Inflects the word so that it agrees with ``num``
        """
        return self.inflect(self.tag.numeral_agreement_grammemes(num))

    @property
    def lexeme(self):
        """ A lexeme this form belongs to. """
        return self._morph.get_lexeme(self)

    @property
    def is_known(self):
        """ True if this form is a known dictionary form. """
        # return self.estimate == 1?
        return self._dict.word_is_known(self.word, strict_ee=True)

    @property
    def normalized(self):
        """ A :class:`Parse` instance for :attr:`self.normal_form`. """
        last_method = self.methods_stack[-1]
        return self.__class__(*last_method[0].normalized(self))

    # @property
    # def paradigm(self):
    #     return self._dict.build_paradigm_info(self.para_id)



class MorphAnalyzer(object):
    """
    Morphological analyzer for Russian language.

    For a given word it can find all possible inflectional paradigms
    and thus compute all possible tags and normal forms.

    Analyzer uses morphological word features and a lexicon
    (dictionary compiled from XML available at OpenCorpora.org);
    for unknown words heuristic algorithm is used.

    Create a :class:`MorphAnalyzer` object::

        >>> import pymorphy2
        >>> morph = pymorphy2.MorphAnalyzer()

    MorphAnalyzer uses dictionaries from ``pymorphy2-dicts`` package
    (which can be installed via ``pip install pymorphy2-dicts``).

    Alternatively (e.g. if you have your own precompiled dictionaries),
    either create ``PYMORPHY2_DICT_PATH`` environment variable
    with a path to dictionaries, or pass ``path`` argument
    to :class:`pymorphy2.MorphAnalyzer` constructor::

        >>> morph = pymorphy2.MorphAnalyzer('/path/to/dictionaries') # doctest: +SKIP

    By default, methods of this class return parsing results
    as namedtuples :class:`Parse`. This has performance implications
    under CPython, so if you need maximum speed then pass
    ``result_type=None`` to make analyzer return plain unwrapped tuples::

        >>> morph = pymorphy2.MorphAnalyzer(result_type=None)

    """

    ENV_VARIABLE = 'PYMORPHY2_DICT_PATH'
    DEFAULT_UNITS = [
        units.DictionaryAnalyzer,

        units.NumberAnalyzer,
        units.PunctuationAnalyzer,
        units.RomanNumberAnalyzer,
        units.LatinAnalyzer,

        units.HyphenSeparatedParticleAnalyzer,
        units.HyphenAdverbAnalyzer,
        units.HyphenatedWordsAnalyzer,
        units.KnownPrefixAnalyzer,
        units.UnknownPrefixAnalyzer,
        units.KnownSuffixAnalyzer,
    ]

    def __init__(self, path=None, result_type=Parse, units=None):

        path = self.choose_dictionary_path(path)
        self.dictionary = opencorpora_dict.Dictionary(path)

        if result_type is not None:
            # create a subclass with the same name,
            # but with _morph attribute bound to self
            res_type = type(
                result_type.__name__,
                (result_type,),
                {'_morph': self, '_dict': self.dictionary}
            )
            self._result_type = res_type
        else:
            self._result_type = None

        self._result_type_orig = result_type

        # initialize units
        if units is None:
            units = self.DEFAULT_UNITS

        self._unit_classes = units
        self._units = [cls(self) for cls in units]


    @classmethod
    def choose_dictionary_path(cls, path=None):
        if path is not None:
            return path

        if cls.ENV_VARIABLE in os.environ:
            return os.environ[cls.ENV_VARIABLE]

        try:
            import pymorphy2_dicts
            return pymorphy2_dicts.get_path()
        except ImportError:
            msg = ("Can't find dictionaries. "
                   "Please either pass a path to dictionaries, "
                   "or install 'pymorphy2-dicts' package, "
                   "or set %s environment variable.") % cls.ENV_VARIABLE
            raise ValueError(msg)


    def parse(self, word):
        """
        Analyze the word and return a list of :class:`pymorphy2.analyzer.Parse`
        namedtuples:

            Parse(word, tag, normal_form, para_id, idx, _estimate)

        (or plain tuples if ``result_type=None`` was used in constructor).
        """
        res = []
        seen = set()
        word_lower = word.lower()

        for analyzer in self._units:
            res.extend(analyzer.parse(word, word_lower, seen))

            if res and analyzer.terminal:
                break

        if self._result_type is None:
            return res

        return [self._result_type(*p) for p in res]


    def tag(self, word):
        res = []
        seen = set()
        word_lower = word.lower()

        for analyzer in self._units:
            res.extend(analyzer.tag(word, word_lower, seen))

            if res and analyzer.terminal:
                break

        return res


    def normal_forms(self, word):
        """
        Return a list of word normal forms.
        """
        seen = set()
        result = []

        for p in self.parse(word):
            normal_form = p[2]
            if normal_form not in seen:
                result.append(normal_form)
                seen.add(normal_form)
        return result

    # ==== inflection ========

    def get_lexeme(self, form):
        """
        Return the lexeme this parse belongs to.
        """
        methods_stack = form[4]
        last_method = methods_stack[-1]
        result = last_method[0].get_lexeme(form)

        if self._result_type is None:
            return result
        return [self._result_type(*p) for p in result]


    def _inflect(self, form, required_grammemes):
        possible_results = [f for f in self.get_lexeme(form)
                            if required_grammemes <= f[1].grammemes]

        if not possible_results:
            required_grammemes = self.TagClass.fix_rare_cases(required_grammemes)
            possible_results = [f for f in self.get_lexeme(form)
                                if required_grammemes <= f[1].grammemes]

        grammemes = form[1].updated_grammemes(required_grammemes)
        def similarity(frm):
            tag = frm[1]
            return len(grammemes & tag.grammemes)

        return heapq.nlargest(1, possible_results, key=similarity)


    # ====== misc =========

    def iter_known_word_parses(self, prefix=""):
        """
        Return an iterator over parses of dictionary words that starts
        with a given prefix (default empty prefix means "all words").
        """

        # XXX: this method currently assumes that
        # units.DictionaryAnalyzer is the first analyzer unit.
        for word, tag, normal_form, para_id, idx in self.dictionary.iter_known_words(prefix):
            methods = ((self._units[0], word, para_id, idx),)
            parse = (word, tag, normal_form, 1.0, methods)
            if self._result_type is None:
                yield parse
            else:
                yield self._result_type(*parse)


    def word_is_known(self, word, strict_ee=False):
        """
        Check if a ``word`` is in the dictionary.
        Pass ``strict_ee=True`` if ``word`` is guaranteed to
        have correct е/ё letters.

        .. note::

            Dictionary words are not always correct words;
            the dictionary also contains incorrect forms which
            are commonly used. So for spellchecking tasks this
            method should be used with extra care.

        """
        return self.dictionary.word_is_known(word.lower(), strict_ee)


    @property
    def TagClass(self):
        """
        :rtype: pymorphy2.tagset.OpencorporaTag
        """
        return self.dictionary.Tag


    def __reduce__(self):
        args = (self.dictionary.path, self._result_type_orig, self._unit_classes)
        return self.__class__, args, None
