#!/usr/bin/env python

from __future__ import print_function

import unittest
from cprnc_py.vardiffs import VarDiffs
import numpy as np
import numpy.ma as ma
from cprnc_py.test_utils.custom_assertions import CustomAssertions

class TestVardiffs(CustomAssertions):

    # ------------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------------

    def create_vardiffs(self, x, y):
        VARNAME = "varname"
        return VarDiffs(VARNAME, x, y)
    
    # ------------------------------------------------------------------------
    # Tests of vars_differ
    # ------------------------------------------------------------------------

    def test_varsDiffer_withIdenticalVars(self):
        x = np.array([1., 2., 3.])
        y = np.array([1., 2., 3.])
        mydiffs = self.create_vardiffs(x, y)

        self.assertFalse(mydiffs.vars_differ())

    def test_varsDiffer_withDifferentVars(self):
        x = np.array([1., 2., 3.])
        y = np.array([1., 2., 4.])
        mydiffs = self.create_vardiffs(x, y)

        self.assertTrue(mydiffs.vars_differ())

    def test_varsDiffer_withMaskedVarsIdentical(self):
        # Masked variables that are identical for points that are not masked out
        # in either array
        x = ma.array([1., 2., 3.], mask=[True,False,False])
        y = ma.array([4., 5., 3.], mask=[False,True,False])
        mydiffs = self.create_vardiffs(x, y)

        self.assertFalse(mydiffs.vars_differ())

    def test_varsDiffer_withDifferentDims(self):
        x = np.array([1,2,3])
        y = np.array([1,2])
        mydiffs = self.create_vardiffs(x, y)

        self.assertFalse(mydiffs.vars_differ())

    # ------------------------------------------------------------------------
    # Tests of masks_differ
    # ------------------------------------------------------------------------
        
    def test_masksDiffer_withUnmaskedVars(self):
        x = np.array([1., 2., 3.])
        y = np.array([1., 2., 4.])
        mydiffs = self.create_vardiffs(x, y)

        self.assertFalse(mydiffs.masks_differ())

    def test_masksDiffer_withOneUnmaskedVarOneMaskFalse(self):
        x = np.array([1., 2., 3.])
        y = ma.array([1., 2., 4.], mask=[False,False,False])
        mydiffs = self.create_vardiffs(x, y)

        self.assertFalse(mydiffs.masks_differ())

    def test_masksDiffer_withOneUnmaskedVarOneMaskTrue(self):
        x = np.array([1., 2., 3.])
        y = ma.array([1., 2., 4.], mask=[False,False,True])
        mydiffs = self.create_vardiffs(x, y)

        self.assertTrue(mydiffs.masks_differ())

    def test_masksDiffer_withMaskedVarsDiffer(self):
        x = ma.array([1., 2., 3.], mask=[True,False,False])
        y = ma.array([1., 2., 3.], mask=[False,True,False])
        mydiffs = self.create_vardiffs(x, y)

        self.assertTrue(mydiffs.masks_differ())

    def test_masksDiffer_withMaskedVarsSame(self):
        x = ma.array([1., 2., 3.], mask=[True,False,False])
        y = ma.array([1., 2., 3.], mask=[True,False,False])
        mydiffs = self.create_vardiffs(x, y)

        self.assertFalse(mydiffs.masks_differ())

    def test_masksDiffer_withDifferentDims(self):
        x = np.array([1,2,3])
        y = np.array([1,2])
        mydiffs = self.create_vardiffs(x, y)

        self.assertFalse(mydiffs.masks_differ())
    
    # ------------------------------------------------------------------------
    # Tests of dims_differ
    # ------------------------------------------------------------------------

    def test_dimsDiffer_withSameDims(self):
        x = np.array([[1,2,3],[4,5,6]])
        y = np.array([[1,2,3],[4,5,6]])
        mydiffs = self.create_vardiffs(x, y)

        self.assertFalse(mydiffs.dims_differ())

    def test_dimsDiffer_withDifferentDims(self):
        x = np.array([[1,2,3],[4,5,6]])
        y = np.array([[1,2],[3,4],[5,6]])
        mydiffs = self.create_vardiffs(x, y)

        self.assertTrue(mydiffs.dims_differ())

    # ------------------------------------------------------------------------
    # Tests of __str__
    # ------------------------------------------------------------------------

    def test_str_differHasRMS(self):
        # If two variables differ, then the resulting string should contain 'RMS'
        x = np.array([1., 2., 3.])
        y = np.array([1., 2., 4.])
        mydiffs = self.create_vardiffs(x, y)

        mystr = str(mydiffs)

        self.assertRegexMatches(mystr, 'RMS')

    def test_str_sameDoesNotHaveRMS(self):
        # If two variables are the same, then the resulting string should not
        # contain 'RMS'
        x = np.array([1., 2., 3.])
        y = np.array([1., 2., 3.])
        mydiffs = self.create_vardiffs(x, y)

        mystr = str(mydiffs)

        self.assertNotRegexMatches(mystr, 'RMS')


if __name__ == '__main__':
    unittest.main()
