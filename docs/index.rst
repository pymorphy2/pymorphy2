Морфологический анализатор pymorphy2
====================================

.. toctree::
   :maxdepth: 2

   user/index
   dev/index
   internals/index
   misc/index

   glossary

pymorphy2_ - наследник pymorphy_. Цели и задачи:

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


.. _pymorphy2: https://github.com/kmike/pymorphy2
.. _pymorphy: https://bitbucket.org/kmike/pymorphy/
.. _OpenCorpora: http://opencorpora.org

Указатели и поиск
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
