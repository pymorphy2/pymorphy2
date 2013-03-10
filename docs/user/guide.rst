.. important:: в примерах используется синтаксис Python 3.

========================
Руководство пользователя
========================

Установка
---------

Для установки воспользуйтесь pip::

    pip install pymorphy2
    pip install pymorphy2-dicts
    pip install DAWG-Python

`pymorphy2-dicts <http://pypi.python.org/pypi/pymorphy2-dicts>`_ - это
пакет со словарями OpenCorpora_, скомпилированными в формат pymorphy2.

Если вы используете CPython (не PyPy), и в системе есть компилятор и т.д.,
то вместо `DAWG-Python`_ можно установить библиотеку DAWG_, которая
позволит pymorphy2 работать быстрее::

    pip install DAWG

.. _DAWG: https://github.com/kmike/DAWG
.. _DAWG-Python: https://github.com/kmike/DAWG-Python
.. _OpenCorpora: http://opencorpora.org/

Морфологический анализ
----------------------

.. py:currentmodule:: pymorphy2.analyzer

Морфологический анализ - это определение характеристик слова
на основе того, как это слово пишется. При морфологическом анализе
**не** используется информация о соседних словах.

В pymorphy2 для морфологического анализа слов (русских) есть
класс :class:`MorphAnalyzer`.

::

    >>> import pymorphy2
    >>> morph = pymorphy2.MorphAnalyzer()

Экземпляры класса :class:`MorphAnalyzer` обычно занимают порядка
10-15Мб оперативной памяти (т.к. загружают в память словари, данные
для предсказателя и т.д.); старайтесь ораганизовать свой код так,
чтоб создавать экземпляр :class:`MorphAnalyzer` заранее и работать
с этим единственным экземпляром в дальнейшем.

С помощью метода :meth:`MorphAnalyzer.parse` можно разобрать слово::

    >>> morph.parse('стали')
    [Parse(word='стали', tag=OpencorporaTag('VERB,perf,intr plur,past,indc'), normal_form='стать', estimate=1.0, methods_stack=((<DictionaryAnalyzer>, 'стали', 883, 4),)),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn sing,gent'), normal_form='сталь', estimate=1.0, methods_stack=((<DictionaryAnalyzer>, 'стали', 12, 1),)),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn sing,datv'), normal_form='сталь', estimate=1.0, methods_stack=((<DictionaryAnalyzer>, 'стали', 12, 2),)),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn sing,loct'), normal_form='сталь', estimate=1.0, methods_stack=((<DictionaryAnalyzer>, 'стали', 12, 5),)),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn plur,nomn'), normal_form='сталь', estimate=1.0, methods_stack=((<DictionaryAnalyzer>, 'стали', 12, 6),)),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn plur,accs'), normal_form='сталь', estimate=1.0, methods_stack=((<DictionaryAnalyzer>, 'стали', 12, 9),))]

.. note::

    если используете Python 2.x, то будьте внимательны - юникодные
    строки пишутся как ``u'стали'``.

В этом примере слово "стали" может быть разобрано и как глагол
("они *стали* лучше справляться"), и как существительное
("кислородно-конверторный способ получения *стали*").
На основе одной лишь информации о том, как слово пишется,
понять, какой разбор правильный, нельзя, поэтому анализатор может
возвращать несколько вариантов разбора.

У каждого разбора есть :term:`нормальная форма <лемма>`, которую можно
получить, обратившись к атрибутам :attr:`normal_form` или :attr:`normalized`::

    >>> p = morph.parse('стали')[0]
    >>> p.normal_form
    'стать'
    >>> p.normalized
    Parse(word='стать', tag=OpencorporaTag('INFN,perf,intr'), normal_form='стать', estimate=1.0, methods_stack=((<DictionaryAnalyzer>, 'стать', 883, 0),))

Кроме того, у каждого разбора есть :term:`тег`::

    >>> p.tag
    OpencorporaTag('VERB,perf,intr plur,past,indc')

Тег - это набор :term:`граммем <граммема>`, характеризующих данное слово.
Например, тег ``'VERB,perf,intr plur,past,indc'`` означает,
что слово - глагол (``VERB``) совершенного вида (``perf``),
непереходный (``intr``), множественного числа (``plur``),
прошедшего времени (``past``), изъявительного наклонения (``indc``).

См. также: :ref:`grammeme-docs`.

pymorphy2 умеет разбирать не только словарные слова; для несловарных слов
автоматически задействуется :ref:`предсказатель <prediction>`. Например,
попробуем разобрать слово "бутявковедами" - pymorphy2 поймет, что это
форма творительного падежа множественного числа существительного
"бутявковед", и что "бутявковед" - одушевленный и мужского рода::

    >>> morph.parse('бутявковедами')
    [Parse(word='бутявковедами', tag=OpencorporaTag('NOUN,anim,masc plur,ablt'), normal_form='бутявковед', estimate=0.49528301886792453, methods_stack=((<FakeDictionary>, 'бутявковедами', 51, 10), (<KnownSuffixAnalyzer>, 'едами')))]


Работа с тегами
---------------

Для того, чтоб проверить, есть ли в данном теге отдельная граммема
(или все граммемы из указанного множества), используйте оператор in::

    >>> 'VERB' in p.tag
    True
    >>> 'NOUN' in p.tag
    False
    >>> {'plur', 'past'} in p.tag
    True
    >>> {'NOUN', 'plur'} in p.tag
    False

.. note::

    Если у вас Python 2.6, то, например, вместо ``{'NOUN', 'plur'}`` нужно
    писать ``set(['NOUN', 'plur'])``.


Кроме того, у каждого тега есть атрибуты, через которые можно получить
часть речи, число и другие характеристики::

    >>> p.tag.POS           # Part of Speech, часть речи
    'VERB'
    >>> p.tag.animacy       # одушевленность
    None
    >>> p.tag.aspect        # вид: совершенный или несовершенный
    'perf'
    >>> p.tag.case          # падеж
    None
    >>> p.tag.gender        # род (мужской, женский, средний)
    None
    >>> p.tag.involvement   # включенность говорящего в действие
    None
    >>> p.tag.mood          # наклонение (повелительное, изъявительное)
    'indc'
    >>> p.tag.number        # число (единственное, множественное)
    'plur'
    >>> p.tag.person        # лицо (1, 2, 3)
    None
    >>> p.tag.tense         # время (настоящее, прошедшее, будущее)
    'past'
    >>> p.tag.transitivity  # переходность (переходный, непереходный)
    'intr'
    >>> p.tag.voice         # залог (действительный, страдательный)
    None

Если запрашиваемая характеристика для данного тега не определена,
то возвращается None.

В написании граммем достаточно просто ошибиться; для борьбы с ошибками
pymorphy2 выкидывает исключение, если встречает недопустимую граммему::

    >>> 'foobar' in p.tag
    Traceback (most recent call last):
    ...
    ValueError: Grammeme is unknown: foobar
    >>> {'NOUN', 'foo', 'bar'} in p.tag
    Traceback (most recent call last):
    ...
    ValueError: Grammemes are unknown: {'bar', 'foo'}

Это работает и для атрибутов::

    >>> p.tag.POS == 'plur'
    Traceback (most recent call last):
    ...
    ValueError: 'plur' is not a valid grammeme for this attribute.

Склонение слов
--------------

pymorphy2 умеет склонять (ставить в какую-то другую форму) слова.
Чтобы просклонять слово, его нужно сначала разобрать - понять, в какой
форме оно стоит в настоящий момент и какая у него :term:`лексема`::

    >>> butyavka = morph.parse('бутявка')[0]
    >>> butyavka
    Parse(word='бутявка', tag=OpencorporaTag('NOUN,inan,femn sing,nomn'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явка', 8, 0), (<UnknownPrefixAnalyzer>, 'бут')))

Для склонения используйте метод :meth:`Parse.inflect`::

    >>> butyavka.inflect({'gent'})  # нет кого? (родительный падеж)
    Parse(word='бутявки', tag=OpencorporaTag('NOUN,inan,femn sing,gent'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явки', 8, 1), (<UnknownPrefixAnalyzer>, 'бут')))
    >>> butyavka.inflect({'plur', 'gent'})  # кого много?
    Parse(word='бутявок', tag=OpencorporaTag('NOUN,inan,femn plur,gent'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явок', 8, 8), (<UnknownPrefixAnalyzer>, 'бут')))

С помощью атрибута :attr:`Parse.lexeme` можно получить лексему слова::

    >>> butyavka.lexeme
    [Parse(word='бутявка', tag=OpencorporaTag('NOUN,inan,femn sing,nomn'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явка', 8, 0), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявки', tag=OpencorporaTag('NOUN,inan,femn sing,gent'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явки', 8, 1), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявке', tag=OpencorporaTag('NOUN,inan,femn sing,datv'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явке', 8, 2), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявку', tag=OpencorporaTag('NOUN,inan,femn sing,accs'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явку', 8, 3), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявкой', tag=OpencorporaTag('NOUN,inan,femn sing,ablt'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явкой', 8, 4), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявкою', tag=OpencorporaTag('NOUN,inan,femn sing,ablt,V-oy'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явкою', 8, 5), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявке', tag=OpencorporaTag('NOUN,inan,femn sing,loct'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явке', 8, 6), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявки', tag=OpencorporaTag('NOUN,inan,femn plur,nomn'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явки', 8, 7), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявок', tag=OpencorporaTag('NOUN,inan,femn plur,gent'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явок', 8, 8), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявкам', tag=OpencorporaTag('NOUN,inan,femn plur,datv'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явкам', 8, 9), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявки', tag=OpencorporaTag('NOUN,inan,femn plur,accs'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явки', 8, 10), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявками', tag=OpencorporaTag('NOUN,inan,femn plur,ablt'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явками', 8, 11), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявках', tag=OpencorporaTag('NOUN,inan,femn plur,loct'), normal_form='бутявка', estimate=0.5, methods_stack=((<DictionaryAnalyzer>, 'явках', 8, 12), (<UnknownPrefixAnalyzer>, 'бут')))]
