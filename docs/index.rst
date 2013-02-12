Морфологический анализатор pymorphy2
====================================

pymorphy2_ - наследник pymorphy_. Цели и задачи:

* поддержка всех возможностей pymorphy_;
* более актуальные и точные словари из OpenCorpora_;
* большая скорость работы (50x-500x) при таком же или меньшем потреблении
  памяти;
* преобразование слов из одной формы в другую между разными частями речи;
* выделение поддержки django в отдельный пакет;
* полная :ref:`поддержка <umlauts>` буквы ё;
* возможность обновления словарей.

.. image:: https://travis-ci.org/kmike/pymorphy2.png?branch=master

Содержание:

.. toctree::
   :maxdepth: 2

   user/index
   dev/index
   internals/index
   misc/index

   CHANGES

   glossary

.. _pymorphy2: https://github.com/kmike/pymorphy2
.. _pymorphy: https://bitbucket.org/kmike/pymorphy/
.. _OpenCorpora: http://opencorpora.org

Указатели и поиск
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
