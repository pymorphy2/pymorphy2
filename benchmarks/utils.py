# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import time
import timeit
import gc

def measure(func, inner_iterations=1, repeats=5):
    """
    Runs func ``repeats`` times and returns the fastest speed
    (inner loop iterations per second). Use ``inner_iterations`` to specify
    the number of inner loop iterations.

    Use this function for long-running functions.
    """
    gc.disable()
    times = []
    for x in range(repeats):
        start = time.time()
        func()
        times.append(time.time() - start)

    gc.enable()
    return inner_iterations/min(times)


def bench(stmt, setup, op_count=1, repeats=3, runs=5):
    """
    Runs ``stmt`` benchmark ``repeats``*``runs`` times,
    selects the fastest run and returns the minimum time.
    """
    timer = timeit.Timer(stmt, setup)
    times = []
    for x in range(runs):
        times.append(timer.timeit(repeats))

    def op_time(t):
        return op_count*repeats / t

    return op_time(min(times))


def format_bench(name, result, description='K words/sec'):
    return "%25s:\t%0.3f%s" % (name, result, description)
