.. important:: в примерах используется синтаксис Python 3.

========================
Руководство пользователя
========================

Установка
---------

Для установки воспользуйтесь pip::

    pip install pymorphy2

Чтоб установить оптимизированную версию, используйте следующую команду::

    pip install pymorphy2[fast]

Оптимизированная версия может требовать настроенного окружения для сборки
(компилятора C/C++ и т.д.).

Словари распространяются отдельными пакетами:

* pymorphy2-dicts-ru для русского языка,
* pymorphy2-dicts-uk для украинского языка (экспериментальный).

Они обновляются время от времени; чтоб обновить словари, используйте

::

    pip install -U pymorphy2-dicts-ru
    pip install -U pymorphy2-dicts-uk

Для установки требуются более-менее современные версии pip и setuptools.

.. _DAWG: https://github.com/kmike/DAWG
.. _DAWG-Python: https://github.com/kmike/DAWG-Python
.. _OpenCorpora: http://opencorpora.org/

Морфологический анализ
----------------------

.. py:currentmodule:: pymorphy2.analyzer

Морфологический анализ - это определение характеристик слова
на основе того, как это слово пишется. При морфологическом анализе
**не** используется информация о соседних словах.

В pymorphy2 для морфологического анализа слов есть
класс :class:`MorphAnalyzer`.

::

    >>> import pymorphy2
    >>> morph = pymorphy2.MorphAnalyzer()

По умолчанию используется словарь для русского языка; чтобы вместо русского
включить украинский словарь, с помощью ``pip`` установите пакет
``pymorphy2-dicts-uk`` и используйте

::

    >>> morph = pymorphy2.MorphAnalyzer(lang='uk')


Экземпляры класса :class:`MorphAnalyzer` обычно занимают порядка
15Мб оперативной памяти (т.к. загружают в память словари, данные
для предсказателя и т.д.); старайтесь организовать свой код так,
чтобы создавать экземпляр :class:`MorphAnalyzer` заранее и работать
с этим единственным экземпляром в дальнейшем.

С помощью метода :meth:`MorphAnalyzer.parse` можно разобрать отдельное слово::

    >>> morph.parse('стали')
    [Parse(word='стали', tag=OpencorporaTag('VERB,perf,intr plur,past,indc'), normal_form='стать', score=0.983766, methods_stack=((<DictionaryAnalyzer>, 'стали', 884, 4),)),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn sing,gent'), normal_form='сталь', score=0.003246, methods_stack=((<DictionaryAnalyzer>, 'стали', 12, 1),)),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn sing,datv'), normal_form='сталь', score=0.003246, methods_stack=((<DictionaryAnalyzer>, 'стали', 12, 2),)),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn sing,loct'), normal_form='сталь', score=0.003246, methods_stack=((<DictionaryAnalyzer>, 'стали', 12, 5),)),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn plur,nomn'), normal_form='сталь', score=0.003246, methods_stack=((<DictionaryAnalyzer>, 'стали', 12, 6),)),
     Parse(word='стали', tag=OpencorporaTag('NOUN,inan,femn plur,accs'), normal_form='сталь', score=0.003246, methods_stack=((<DictionaryAnalyzer>, 'стали', 12, 9),))]

.. note::

    если используете Python 2.x, то будьте внимательны - юникодные
    строки пишутся как ``u'стали'``.

Метод :meth:`MorphAnalyzer.parse` возвращает один или несколько
объектов типа :class:`~.Parse` с информацией о том, как слово может быть
разобрано.

В приведенном примере слово "стали" может быть разобрано и как глагол
("они *стали* лучше справляться"), и как существительное
("кислородно-конверторный способ получения *стали*").
На основе одной лишь информации о том, как слово пишется,
понять, какой разбор правильный, нельзя, поэтому анализатор может
возвращать несколько вариантов разбора.

У каждого разбора есть :term:`тег`::

    >>> p = morph.parse('стали')[0]
    >>> p.tag
    OpencorporaTag('VERB,perf,intr plur,past,indc')

Тег - это набор :term:`граммем <граммема>`, характеризующих данное слово.
Например, тег ``'VERB,perf,intr plur,past,indc'`` означает,
что слово - глагол (``VERB``) совершенного вида (``perf``),
непереходный (``intr``), множественного числа (``plur``),
прошедшего времени (``past``), изъявительного наклонения (``indc``).

Доступные граммемы описаны тут: :ref:`grammeme-docs`.

Кроме того, у каждого разбора есть :term:`нормальная форма <лемма>`,
которую можно получить, обратившись к атрибутам :attr:`normal_form`
или :attr:`normalized`::

    >>> p.normal_form
    'стать'
    >>> p.normalized
    Parse(word='стать', tag=OpencorporaTag('INFN,perf,intr'), normal_form='стать', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'стать', 884, 0),))

.. note::

    См. также: :ref:`normalization`.

pymorphy2 умеет разбирать не только словарные слова; для несловарных слов
автоматически задействуется :ref:`предсказатель <prediction>`. Например,
попробуем разобрать слово "бутявковедами" - pymorphy2 поймет, что это
форма творительного падежа множественного числа существительного
"бутявковед", и что "бутявковед" - одушевленный и мужского рода::

    >>> morph.parse('бутявковедами')
    [Parse(word='бутявковедами', tag=OpencorporaTag('NOUN,anim,masc plur,ablt'), normal_form='бутявковед', score=1.0, methods_stack=((<FakeDictionary>, 'бутявковедами', 51, 10), (<KnownSuffixAnalyzer>, 'едами')))]


Работа с тегами
---------------

Для того, чтоб проверить, есть ли в данном теге отдельная граммема
(или все граммемы из указанного множества), используйте оператор in::

    >>> p.tag
    OpencorporaTag('VERB,perf,intr plur,past,indc')
    >>> 'NOUN' in p.tag  # то же самое, что и {'NOUN'} in p.tag
    False
    >>> 'VERB' in p.tag
    True
    >>> {'VERB'} in p.tag
    True
    >>> {'plur', 'past'} in p.tag
    True
    >>> {'NOUN', 'plur'} in p.tag
    False

Кроме того, у каждого тега есть атрибуты, через которые можно получить
часть речи, число и другие характеристики::

    >>> p.tag
    OpencorporaTag('VERB,perf,intr plur,past,indc')
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


Кириллические названия тегов и граммем
--------------------------------------

Теги и граммемы в pymorphy2 записываются латиницей (например, ``NOUN``).
Но часто удобнее использовать кириллические названия граммем (например,
``СУЩ`` вместо ``NOUN``). Чтобы получить тег в виде строки,
записанной кириллицей, используйте свойство :attr:`OpencorporaTag.cyr_repr`::

    >>> p.tag
    OpencorporaTag('VERB,perf,intr plur,past,indc')
    >>> p.tag.cyr_repr
    'ГЛ,сов,неперех мн,прош,изъяв'

Для преобразования произвольных строк с тегами/граммемами между
кириллицей и латиницей используйте методы :meth:`MorphAnalyzer.cyr2lat`
и :meth:`MorphAnalyzer.lat2cyr`::

    >>> morph.lat2cyr('NOUN,anim,masc plur,ablt')
    'СУЩ,од,мр мн,тв'
    >>> morph.cyr2lat('СУЩ,од,мр мн,тв')
    'NOUN,anim,masc plur,ablt'

.. _inflection:

Склонение слов
--------------

pymorphy2 умеет склонять (ставить в какую-то другую форму) слова.
Чтобы просклонять слово, нужно сначала понять, в какой форме оно
стоит в настоящий момент и какая у него :term:`лексема`.
Другими словами, нужно сперва разобрать слово и выбрать из предложенных
вариантов разбора правильный.

Для примера разберем слово "бутявка" и возьмем первый вариант разбора::

    >>> butyavka = morph.parse('бутявка')[0]
    >>> butyavka
    Parse(word='бутявка', tag=OpencorporaTag('NOUN,inan,femn sing,nomn'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явка', 8, 0), (<UnknownPrefixAnalyzer>, 'бут')))

Получив объект :class:`~.Parse`, можно просклонять слово, используя
его метод :meth:`Parse.inflect`::

    >>> butyavka.inflect({'gent'})  # нет кого? (родительный падеж)
    Out[13]:
    Parse(word='бутявки', tag=OpencorporaTag('NOUN,inan,femn sing,gent'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явки', 8, 1), (<UnknownPrefixAnalyzer>, 'бут')))
    >>> butyavka.inflect({'plur', 'gent'})  # кого много?
    Parse(word='бутявок', tag=OpencorporaTag('NOUN,inan,femn plur,gent'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явок', 8, 8), (<UnknownPrefixAnalyzer>, 'бут')))

С помощью атрибута :attr:`Parse.lexeme` можно получить лексему слова::

    >>> butyavka.lexeme
    [Parse(word='бутявка', tag=OpencorporaTag('NOUN,inan,femn sing,nomn'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явка', 8, 0), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявки', tag=OpencorporaTag('NOUN,inan,femn sing,gent'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явки', 8, 1), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявке', tag=OpencorporaTag('NOUN,inan,femn sing,datv'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явке', 8, 2), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявку', tag=OpencorporaTag('NOUN,inan,femn sing,accs'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явку', 8, 3), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявкой', tag=OpencorporaTag('NOUN,inan,femn sing,ablt'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явкой', 8, 4), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявкою', tag=OpencorporaTag('NOUN,inan,femn sing,ablt,V-oy'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явкою', 8, 5), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявке', tag=OpencorporaTag('NOUN,inan,femn sing,loct'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явке', 8, 6), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявки', tag=OpencorporaTag('NOUN,inan,femn plur,nomn'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явки', 8, 7), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявок', tag=OpencorporaTag('NOUN,inan,femn plur,gent'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явок', 8, 8), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявкам', tag=OpencorporaTag('NOUN,inan,femn plur,datv'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явкам', 8, 9), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявки', tag=OpencorporaTag('NOUN,inan,femn plur,accs'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явки', 8, 10), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявками', tag=OpencorporaTag('NOUN,inan,femn plur,ablt'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явками', 8, 11), (<UnknownPrefixAnalyzer>, 'бут'))),
     Parse(word='бутявках', tag=OpencorporaTag('NOUN,inan,femn plur,loct'), normal_form='бутявка', score=1.0, methods_stack=((<DictionaryAnalyzer>, 'явках', 8, 12), (<UnknownPrefixAnalyzer>, 'бут')))]

.. _normalization:

Постановка слов в начальную форму
---------------------------------

Нормальную (начальную) форму слова можно получить через атрибуты
:attr:`Parse.normal_form` и :attr:`Parse.normalized`. Чтоб получить
объект :class:`~.Parse`, нужно сперва разобрать слово и выбрать правильный
вариант разбора из предложенных.

Но что считается за нормальную форму? Например, возьмем слово "думающим".
Иногда мы захотим нормализовать его в "думать", иногда - в "думающий",
иногда - в "думающая".

Посмотрим, что сделает pymorphy2 в этом примере:

    >>> morph.parse('думающему')[0].normal_form
    'думать'

pymorphy2 сейчас использует алгоритм нахождения нормальной формы,
который работает наиболее быстро (берется первая форма
в :term:`лексеме <лексема>`) - поэтому, например, все причастия сейчас
нормализуются в инфинитивы. Это можно считать деталью реализации.

Если требуется нормализовывать слова иначе, можно воспользоваться
методом :meth:`Parse.inflect`::

    >>> morph.parse('думающему')[0].inflect({'sing', 'nomn'}).word
    'думающий'

Согласование слов с числительными
---------------------------------

Слово нужно ставить в разные формы в зависимости от числительного,
к которому оно относится. Например: "1 бутявка", "2 бутявки", "5 бутявок"

Для этих целей используйте метод :meth:`Parse.make_agree_with_number`::

    >>> butyavka = morph.parse('бутявка')[0]
    >>> butyavka.make_agree_with_number(1).word
    'бутявка'
    >>> butyavka.make_agree_with_number(2).word
    'бутявки'
    >>> butyavka.make_agree_with_number(5).word
    'бутявок'

В винительном падеже согласование с числительными зависит от одушевленности, но граммема одушевленности может присутствовать в теге не всегда (например, у прилагательных).
В этом случае одушевленность можно явно указать в параметре `animacy`, значение которого используется в случае отсутствися соответствующей граммемы.

    >>> noun = next(x for x in morph.parse('пуська') if x.tag.POS == 'NOUN')
    >>> noun.tag.animacy
    'anim'
    >>> adjf = next(x for x in morph.parse('бятая') if x.tag.POS == 'ADJF')
    >>> adjf.tag.animacy
    >>> adjf.inflect({'accs'}).make_agree_with_number(2).word
    'бятые'
    >>> adjf.inflect({'accs'}).make_agree_with_number(2, animacy='anim').word
    'бятых'
    >>> noun.inflect({'accs'}).make_agree_with_number(2).word
    'пусек'

.. _select-correct:

Выбор правильного разбора
-------------------------

pymorphy2 возвращает все допустимые варианты разбора, но на практике
обычно нужен только один вариант, правильный.

У каждого разбора есть параметр score::

    >>> morph.parse('на')
    [Parse(word='на', tag=OpencorporaTag('PREP'), normal_form='на', score=0.999628, methods_stack=((<DictionaryAnalyzer>, 'на', 23, 0),)),
     Parse(word='на', tag=OpencorporaTag('INTJ'), normal_form='на', score=0.000318, methods_stack=((<DictionaryAnalyzer>, 'на', 20, 0),)),
     Parse(word='на', tag=OpencorporaTag('PRCL'), normal_form='на', score=5.3e-05, methods_stack=((<DictionaryAnalyzer>, 'на', 21, 0),))]

score - это оценка P(tag|word), оценка вероятности того, что данный
разбор правильный.

.. note::

    Оценка P(tag|word) пока недоступна в украинском словаре.

Условная вероятность P(tag|word) оценивается на основе корпуса OpenCorpora_:
ищутся все неоднозначные слова со снятой неоднозначностью, для каждого слова
считается, сколько раз ему был сопоставлен данный тег, и на основе этих частот
вычисляется условная вероятность тега (с использованием сглаживания Лапласа).

На данный момент оценки P(tag|word) на основе OpenCorpora есть
примерно для 20 тыс. слов (исходя из примерно 250тыс. наблюдений).
Для тех слов, для которых такой оценки нет, вероятность P(tag|word) либо
считается равномерной (для словарных слов), либо оценивается на основе
эмпирических правил (для несловарных слов).

На практике это означает, что первый разбор из тех, что возвращают методы
:meth:`MorphAnalyzer.parse` и :meth:`MorphAnalyzer.tag`, более вероятен,
чем остальные. Для слов (без учета пунктуации и т.д.) цифры такие:

* случайно выбранный разбор (из допустимых) верен примерно в **66%** случаев;
* первый по словарю разбор (pymorphy2 < 0.4) верен примерно в **72%** случаев;
* разбор, который выдает pymorphy2 == 0.4, выбранный на основе
  оценки P(tag|word), верен примерно в **79%** случаев.

Разборы сортируются по убыванию score, поэтому везде в примерах берется
первый вариант разбора из возможных (например, ``morph.parse('бутявка')[0]``).

Оценки P(tag|word) помогают улучшить разбор, но их недостаточно для
надежного снятия неоднозначности, как минимум по следующим причинам:

* то, как нужно разбирать слово, зависит от соседних слов; pymorphy2 работает
  только на уровне отдельных слов;
* условная вероятность P(tag|word) оценена на основе сбалансированного
  набора текстов; в специализированных текстах вероятности могут быть другими -
  например, возможно, что в металлургических текстах
  ``P(NOUN|стали) > P(VERB|стали)``;
* в OpenCorpora у большинства слов неоднозначность пока не снята; выполняя
  задания на сайте OpenCorpora_, можно непосредственно помочь улучшить
  оценку P(tag|word) и, следовательно, качество работы pymorphy2.

Если вы берете первый разбор из возможных (как в примерах), то стоит
учитывать эту проблему.

Иногда могут помочь какие-то особенности задачи. Например, если нужно
просклонять слово, и известно, что на входе ожидается слово в именительном
падеже, то лучше брать вариант разбора в именительном падеже, а не первый.
В общем же случае для выбора точного разбора необходимо каким-то образом
учитывать не только само слово, но и другие слова в предложении.
