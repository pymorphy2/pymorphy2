# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging

import pytest
import docopt

from pymorphy2 import cli


def run_pymorphy2(args=(), stdin=None):
    cli.main(args)


def test_show_usage():
    with pytest.raises(docopt.DocoptExit) as e:
        run_pymorphy2([])
    assert 'Usage:' in str(e.value)


def test_show_memory_usage(capsys):
    pytest.importorskip("psutil")

    run_pymorphy2(['dict', 'mem_usage'])
    out = ' '.join(capsys.readouterr())
    assert 'Memory usage:' in out


def test_show_dict_meta(capsys, morph):
    meta = morph.dictionary.meta
    run_pymorphy2(['dict', 'meta'])
    out = ' '.join(capsys.readouterr())
    assert meta['compiled_at'] in out


def test_parse_basic(tmpdir, capsys):
    logging.raiseExceptions = False
    try:
        p = tmpdir.join('words.txt')
        p.write_text(u"""
        крот пришел
        """, encoding='utf8')
        run_pymorphy2(["parse", str(p)])
        out, err = capsys.readouterr()
        print(out)
        print(err)
        assert out.strip() == u"""
крот{крот:1.000=NOUN,anim,masc sing,nomn}
пришел{прийти:1.000=VERB,perf,intr masc,sing,past,indc}
        """.strip()
    finally:
        logging.raiseExceptions = True
