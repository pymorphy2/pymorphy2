# -*- coding: utf-8 -*-
"""
Constants and configuration for Ukrainian language.
"""
from __future__ import absolute_import, unicode_literals
from pymorphy2 import units

# paradigm prefixes used for dictionary compilation
PARADIGM_PREFIXES = ["", "най", "якнай", "щонай"]

# letters initials can start with
INITIAL_LETTERS = 'АБВГҐДЕЄЖЗІЇЙКЛМНОПРСТУФХЦЧШЩЮЯ'

# a list of particles which can be attached to a word using a hyphen
PARTICLES_AFTER_HYPHEN = ["-таки"]  # TODO: check this list

# "ґ" is sometimes written as "г", but not the other way around
CHAR_SUBSTITUTES = {'г': 'ґ'}

# Prefixes which don't change the word parse.
# The list is based on
# https://github.com/languagetool-org/languagetool/blob/master/languagetool-language-modules/uk/src/main/resources/org/languagetool/resource/uk/dash_prefixes.txt
# TODO: prefixes without a hyphen?
KNOWN_PREFIXES = [
    "3g-",
    "3d-",
    "2g-",
    "2d-",
    "4d-",
    "4g-",
    "cad-",
    "cd-",
    "ddos-",
    "dos-",
    "dvd-",
    "e-",
    "fm-",
    "gprs-",
    "gps-",
    "gsm-",
    "hd-",
    "ip-",
    "it-",
    "lcd-",
    "lng-",
    "mp3-",
    "pin-",
    "pr-",
    "r&b-",
    "r&d-",
    "sim-",
    "sms-",
    "vip-",
    "x-",
    "y-",
    "альфа-",
    "арт-",
    "аудіо-",
    "байкер-",
    "бард-",
    "бас-",
    "бета-",
    "бізнес-",
    "блок-",
    "блюз-",
    "вакуум-",
    "веб-",
    "віл-",
    "віп-",
    "віце-",
    "гала-",
    "гамма-",
    "гей-",
    "генерал-",
    "гольф-",
    "горе-",
    "гранд-",
    "дельта-",
    "джаз-",
    "диво-",
    "дизайн-",
    "дизель-",
    "допінг-",
    "драг-",
    "е-",
    "економ-",
    "екс-",
    "експрес-",
    "ерзац-",
    "євро-",
    "зомбі-",
    "імідж-",
    "інді-",
    "інтернет-",
    "історико-",
    "іт-",
    "йога-",
    "кібер-",
    "кітч-",
    "контент-",
    "конференц-",
    "концепт-",
    "кремль-",
    "крос-",
    "лейб-",
    "люкс-",
    "максі-",
    "медіа-",
    "міді-",
    "міні-",
    "націонал-",
    "обер-",
    "онлайн-",
    "офіс-",
    "панк-",
    "піар-",
    "поп-",
    "прем'єр-",
    "прес-",
    "рентген-",
    "реп-",
    "ритм-",
    "рок-",
    "салон-",
    "саунд-",
    "секс-",
    "скінхед-",
    "смарт-",
    "соціал-",
    "спам-",
    "спаринг-",
    "тату-",
    "тест-",
    "топ-",
    "торент-",
    "тренд-",
    "тур-",
    "ура-",
    "фан-",
    "фітнес-",
    "флеш-",
    "фолк-",
    "хеш-",
    "цар-",
    "чудо-",
    "шопінг-",
    "шоу-",
    "штаб-",
]

# default analyzer units
DEFAULT_UNITS = [
    [
        units.DictionaryAnalyzer(),
        units.AbbreviatedFirstNameAnalyzer(INITIAL_LETTERS),
        units.AbbreviatedPatronymicAnalyzer(INITIAL_LETTERS),

        # "I" can be a Roman number or an English word
        units.RomanNumberAnalyzer(),
        units.LatinAnalyzer()
    ],

    units.NumberAnalyzer(),
    units.PunctuationAnalyzer(),

    units.HyphenSeparatedParticleAnalyzer(PARTICLES_AFTER_HYPHEN),
    units.HyphenatedWordsAnalyzer(skip_prefixes=KNOWN_PREFIXES),
    units.KnownPrefixAnalyzer(known_prefixes=KNOWN_PREFIXES),
    [
        units.UnknownPrefixAnalyzer(),
        units.KnownSuffixAnalyzer()
    ],
    units.UnknAnalyzer(),
]
