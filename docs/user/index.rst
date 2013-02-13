===========
Руководство
===========

pymorphy2 - морфологический анализатор для русского языка, написанный
на языке Python и использующий словари из OpenCorpora_. Он работает
под Python 2.6, 2.7, 3.2 и 3.3 и распространяется по лицензии MIT.

Исходный код можно получить на github_ или bitbucket_. Если заметили
ошибку - пишите в `баг-трекер`_ (на github). Для обсуждения есть
`гугл-группа`_; если есть какие-то вопросы - пишите туда.

.. _github: https://github.com/kmike/pymorphy2
.. _bitbucket: https://bitbucket.org/kmike/pymorphy2
.. _баг-трекер: https://github.com/kmike/pymorphy2/issues
.. _гугл-группа: https://groups.google.com/forum/?fromgroups#!forum/pymorphy

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

.. note::

    В документации в примерах используется синтаксис Python 3.x.

    Если у вас Python 2.6, вместо ``{'NOUN', 'plur'}``
    используйте ``set(['NOUN', 'plur'])``. Кроме того, под 2.x
    будьте внимательны - юникодные строки пишутся как ``u'строка'``.



.. py:currentmodule:: pymorphy2.analyzer

Морфологический анализ - это определение характеристик слова
на основе того, как это слово пишется. При морфологическом анализе
**не** используется информация о соседних словах.

В pymorphy2 для морфологического анализа слов (русских) есть
класс :class:`MorphAnalyzer`.

::

    >>> import pymorphy2
    >>> morph = pymorphy2.MorphAnalyzer()

Экземпляры класса :class:`MorphAnalyzer` занимают порядка 10-15Мб оперативной
памяти (т.к. загружают в память словари, данные для предсказателя и т.д.);
старайтесь ораганизовать свой код так, чтоб создавать экземпляр
:class:`MorphAnalyzer` заранее и работать с этим единственным экземпляром
в дальнейшем.

Метод :meth:`MorphAnalyzer.parse` принимает слово
(обязательно в нижнем регистре) и возвращает все возможные разборы слова:

    >>> morph.parse('стали')
    [Parse(word='стали', tag=OpencorporaTag('VERB,perf,intr plur,past,indc'), normal_form='стать', para_id=879, idx=4, estimate=1.0),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn sing,gent'), normal_form='сталь', para_id=12, idx=1, estimate=1.0),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn sing,datv'), normal_form='сталь', para_id=12, idx=2, estimate=1.0),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn sing,loct'), normal_form='сталь', para_id=12, idx=5, estimate=1.0),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn plur,nomn'), normal_form='сталь', para_id=12, idx=6, estimate=1.0),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn plur,accs'), normal_form='сталь', para_id=12, idx=9, estimate=1.0)]

.. note::

    обратите внимание, что в этом примере слово "стали" может быть
    разобрано и как глагол ("они *стали* лучше справляться"),
    и как существительное ("кислородно-конверторный способ получения *стали*").
    На основе одной лишь информации о том, как слово пишется,
    понять, какой разбор правильный, нельзя, поэтому анализатор может
    возвращать несколько вариантов разбора.

pymorphy2 умеет разбирать не только словарные слова; для несловарных слов
автоматически задействуется :ref:`предсказатель <prediction>`. Например,
попробуем разобрать слово "бутявковедами" - pymorphy2 поймет, что это
форма творительного падежа множественного числа существительного
"бутявковед", и что "бутявковед" - одушевленный и мужского рода::

    >>> morph.parse('бутявковедами')
    [Parse(word='бутявковедами', tag=OpencorporaTag('NOUN,anim,masc plur,ablt'), normal_form='бутявковед', para_id=51, idx=10, estimate=0.49528301886792453)]

У каждого разбора есть :term:`нормальная форма <лемма>`, которую можно
получить, обратившись к атрибутам :attr:`normal_form` или :attr:`normalized`::

    >>> p = morph.parse('стали')[0]
    >>> p.normal_form
    'стать'
    >>> p.normalized
    Parse(word='стать', tag=OpencorporaTag('INFN,perf,intr'), normal_form='стать', para_id=879, idx=0, estimate=1.0)

Кроме того, у каждого разбора есть :term:`тег`::

    >>> p.tag
    OpencorporaTag('VERB,perf,intr plur,past,indc')

Тег - это набор :term:`граммем <граммема>`, характеризующих данное слово.
Например, тег ``'VERB,perf,intr plur,past,indc'`` означает,
что слово - глагол (``VERB``) совершенного вида (``perf``),
непереходный (``intr``), множественного числа (``plur``),
прошедшего времени (``past``), изъявительного наклонения (``indc``).

pymorphy2 использует теги и граммемы OpenCorpora.
Полный набор допустимых граммем и то, что они означают, можно
посмотреть по этой ссылке: http://opencorpora.org/dict.php?act=gram

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

Если характеристика для данного тега не определена, то возвращается None.

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
форме оно стоит в настоящий момент::

    >>> butyavka = morph.parse('бутявка')[0]
    >>> butyavka
    Parse(word='бутявка', tag=OpencorporaTag('NOUN,inan,femn sing,nomn'), normal_form='бутявка', para_id=8, idx=0, estimate=0.5)

Для склонения используйте метод ``inflect``::

    >>> butyavka.inflect({'gent'}) # нет кого? (родительный падеж)
    Parse(word='бутявки', tag=OpencorporaTag('NOUN,inan,femn sing,gent'), normal_form='бутявка', para_id=8, idx=1, estimate=0.5)
    >>> butyavka.inflect({'plur', 'gent'}) # кого много?
    Parse(word='бутявок', tag=OpencorporaTag('NOUN,inan,femn plur,gent'), normal_form='бутявка', para_id=8, idx=8, estimate=0.5)

С помощью атрибута :attr:`lexeme` можно получить :term:`лексему <лексема>`
слова::

    >>> butyavka.lexeme
    [Parse(word='бутявка', tag=OpencorporaTag('NOUN,inan,femn sing,nomn'), normal_form='бутявка', para_id=8, idx=0, estimate=0.5),
     Parse(word='бутявки', tag=OpencorporaTag('NOUN,inan,femn sing,gent'), normal_form='бутявка', para_id=8, idx=1, estimate=0.5),
     Parse(word='бутявке', tag=OpencorporaTag('NOUN,inan,femn sing,datv'), normal_form='бутявка', para_id=8, idx=2, estimate=0.5),
     Parse(word='бутявку', tag=OpencorporaTag('NOUN,inan,femn sing,accs'), normal_form='бутявка', para_id=8, idx=3, estimate=0.5),
     Parse(word='бутявкой', tag=OpencorporaTag('NOUN,inan,femn sing,ablt'), normal_form='бутявка', para_id=8, idx=4, estimate=0.5),
     Parse(word='бутявкою', tag=OpencorporaTag('NOUN,inan,femn sing,ablt,V-oy'), normal_form='бутявка', para_id=8, idx=5, estimate=0.5),
     Parse(word='бутявке', tag=OpencorporaTag('NOUN,inan,femn sing,loct'), normal_form='бутявка', para_id=8, idx=6, estimate=0.5),
     Parse(word='бутявки', tag=OpencorporaTag('NOUN,inan,femn plur,nomn'), normal_form='бутявка', para_id=8, idx=7, estimate=0.5),
     Parse(word='бутявок', tag=OpencorporaTag('NOUN,inan,femn plur,gent'), normal_form='бутявка', para_id=8, idx=8, estimate=0.5),
     Parse(word='бутявкам', tag=OpencorporaTag('NOUN,inan,femn plur,datv'), normal_form='бутявка', para_id=8, idx=9, estimate=0.5),
     Parse(word='бутявки', tag=OpencorporaTag('NOUN,inan,femn plur,accs'), normal_form='бутявка', para_id=8, idx=10, estimate=0.5),
     Parse(word='бутявками', tag=OpencorporaTag('NOUN,inan,femn plur,ablt'), normal_form='бутявка', para_id=8, idx=11, estimate=0.5),
     Parse(word='бутявках', tag=OpencorporaTag('NOUN,inan,femn plur,loct'), normal_form='бутявка', para_id=8, idx=12, estimate=0.5)]
