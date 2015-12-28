#!/usr/bin/env python

from __future__ import print_function

import unittest
from print_utils import index_str

class TestPrintUtils(unittest.TestCase):

    # ------------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------------

    @staticmethod
    def remove_spaces(string):
        """Return a string that is equivalent to the passed-in string, but with
        spaces removed.

        This is useful for testing, so that tests won't fail if we change the
        output format slightly."""

        return string.replace(" ", "")

    # ------------------------------------------------------------------------
    # Tests of index_str
    # ------------------------------------------------------------------------

    def test_indexStr_with0d(self):
        result = index_str(())
        self.assertEqual(self.remove_spaces(result), "")

    def test_indexStr_with1d(self):
        result = index_str((17,))
        self.assertEqual(self.remove_spaces(result), "(17)")

    def test_indexStr_with3d(self):
        result = index_str((2,3,4))
        self.assertEqual(self.remove_spaces(result), "(2,3,4)")

if __name__ == '__main__':
    unittest.main()

