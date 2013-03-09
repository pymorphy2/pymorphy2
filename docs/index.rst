Морфологический анализатор pymorphy2
====================================

.. toctree::
   :maxdepth: 2

   user/index
   internals/index
   misc/index

   glossary


pymorphy2_ - морфологический анализатор для русского языка
(наследник pymorphy_), написанный на языке Python и использующий
словари из OpenCorpora_. Он работает под Python 2.6, 2.7, 3.2 и 3.3
и распространяется по лицензии MIT.

Исходный код можно получить на github_ или bitbucket_. Если заметили
ошибку - пишите в `баг-трекер`_. Для обсуждения есть `гугл-группа`_;
если есть какие-то вопросы - пишите туда.

Цели и задачи:

* поддержка всех возможностей pymorphy_ **(не готово)**;
* более актуальные и точные словари из OpenCorpora_;
* большая скорость работы (50x-500x) при таком же или меньшем потреблении
  памяти;
* преобразование слов из одной формы в другую между разными частями речи;
* выделение поддержки django в отдельный пакет **(не готово)**;
* полная :ref:`поддержка <umlauts>` буквы ё;
* возможность обновления словарей;
* ранжирование результатов разбора **(готово только частично)**;
* снятие неоднозначности разбора (?) **(не готово)**.


.. _github: https://github.com/kmike/pymorphy2
.. _bitbucket: https://bitbucket.org/kmike/pymorphy2
.. _баг-трекер: https://github.com/kmike/pymorphy2/issues
.. _гугл-группа: https://groups.google.com/forum/?fromgroups#!forum/pymorphy
.. _pymorphy2: https://github.com/kmike/pymorphy2
.. _pymorphy: https://bitbucket.org/kmike/pymorphy/
.. _OpenCorpora: http://opencorpora.org

Указатели и поиск
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
