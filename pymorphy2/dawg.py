# -*- coding: utf-8 -*-
from __future__ import absolute_import

try:
    import dawg
    CAN_CREATE = True

except ImportError:
    import dawg_python as dawg
    CAN_CREATE = False


class WordsDawg(dawg.RecordDAWG):
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
            if not CAN_CREATE:
                raise NotImplementedError("Creating of DAWGs with DAWG-Python is not supported; install 'dawg' package. ")
            super(WordsDawg, self).__init__(self.DATA_FORMAT, data)
