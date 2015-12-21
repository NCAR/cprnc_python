#!/usr/bin/env python

from __future__ import print_function

import unittest
from vardiffs import VarDiffs
import numpy as np

class TestVardiffs(unittest.TestCase):

    def test_varsDiffer_withIdenticalVars(self):
        x = np.array([1., 2., 3.])
        y = np.array([1., 2., 3.])
        mydiffs = VarDiffs(x, y)

        self.assertFalse(mydiffs.vars_differ())

    def test_varsDiffer_withDifferentVars(self):
        x = np.array([1., 2., 3.])
        y = np.array([1., 2., 4.])
        mydiffs = VarDiffs(x, y)

        self.assertTrue(mydiffs.vars_differ())
        
        
if __name__ == '__main__':
    unittest.main()
