#!/usr/bin/env python

from __future__ import print_function

import unittest
import numpy as np
import numpy.ma as ma
from cprnc_py.test_utils.custom_assertions import CustomAssertions
from cprnc_py.netcdf.netcdf_utils import apply_fillvalue

class TestNetcdfUtils(CustomAssertions):

    # ------------------------------------------------------------------------
    # Tests of apply_fillvalue
    # ------------------------------------------------------------------------

    def test_applyFillvalue_withNoFill(self):
        result = apply_fillvalue(data = np.array([1,2,3]),
                                 attributes = {})
        self.assertArraysEqual(result, ma.array([1,2,3]))

    def test_applyFillvalue_withFillValue(self):
        result = apply_fillvalue(data = np.array([1,2,3]),
                                 attributes = {'_FillValue':2})
        self.assertArraysEqual(result, ma.array([1,2,3], mask=[False,True,False]))

    def test_applyFillvalue_withMissingValue(self):
        result = apply_fillvalue(data = np.array([1,2,3]),
                                 attributes = {'missing_value':2})
        self.assertArraysEqual(result, ma.array([1,2,3], mask=[False,True,False]))

    def test_applyFillvalue_withFillAndMissingValue(self):
        result = apply_fillvalue(data = np.array([1,2,3]),
                                 attributes = {'missing_value':1,
                                               '_FillValue':2})
        self.assertArraysEqual(result, ma.array([1,2,3], mask=[False,True,False]))

if __name__ == '__main__':
    unittest.main()
