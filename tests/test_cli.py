# -*- coding: utf-8 -*-
from __future__ import absolute_import
import pytest
import docopt

from pymorphy2 import cli
from .utils import morph


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


def test_show_dict_meta(capsys):
    meta = morph.dictionary.meta
    run_pymorphy2(['dict', 'meta'])
    out = ' '.join(capsys.readouterr())
    assert meta['compiled_at'] in out
