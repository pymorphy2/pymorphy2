#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pymorphy2 benchmark utility.

Usage:
    bench.py run [--verbose]
    bench.py -h | --help
    bench.py --version

Options:
    -v --verbose        Be more verbose

"""
import logging
import sys
import os
from pymorphy2.vendor.docopt import docopt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pymorphy2

from benchmarks import speed

logger = logging.getLogger('pymorphy2.bench')
logger.addHandler(logging.StreamHandler())


def main():
    """ CLI interface dispatcher """
    args = docopt(__doc__, version=pymorphy2.__version__)

    if args['--verbose']:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if args['run']:
        speed.bench_all()

    #logger.debug(args)
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())