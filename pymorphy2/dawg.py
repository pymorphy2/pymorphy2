# -*- coding: utf-8 -*-
from __future__ import absolute_import

try:
    from dawg import DAWG, RecordDAWG
    CAN_CREATE = True

except ImportError:
    from dawg_python import DAWG, RecordDAWG
    CAN_CREATE = False

def assert_can_create():
    if not CAN_CREATE:
        msg = ("Creating of DAWGs with DAWG-Python is "
               "not supported; install 'dawg' package.")
        raise NotImplementedError(msg)


class WordsDawg(RecordDAWG):
    """
    DAWG for storing words.
    """

    # We are storing 2 unsigned short ints as values:
    # the paradigm ID and the form index (inside paradigm).
    # Byte order is big-endian (this makes word forms properly sorted).
    DATA_FORMAT = str(">HH")

    def __init__(self, data=None):
        if data is None:
            super(WordsDawg, self).__init__(self.DATA_FORMAT)
        else:
            assert_can_create()
            super(WordsDawg, self).__init__(self.DATA_FORMAT, data)

class PredictionSuffixesDAWG(WordsDawg):
    """
    DAWG for storing prediction data.
    """

    # We are storing 3 unsigned short ints as values:
    # count, the paradigm ID and the form index (inside paradigm).
    # Byte order is big-endian (this makes word forms properly sorted).
    DATA_FORMAT = str(">HHH")
