#!/usr/bin/env python

import unittest
from cprnc_py.test_utils.custom_assertions import CustomAssertions
import numpy as np
import numpy.ma as ma

class TestCustomAssertions(CustomAssertions):

    def test_ArraysEqual_withEqualArrays(self):
        x = np.array([1., 2., 3.])
        y = np.array([1., 2., 3.])
        self.assertArraysEqual(x,y)
        # Test passes if assertion passes

    def test_ArraysEqual_withDifferentShapes(self):
        x = np.array([1,2,3])
        y = np.array([1,2])
        self.assertRaises(AssertionError, self.assertArraysEqual, x, y)

    def test_ArraysEqual_withDifferentArrays(self):
        x = np.array([1., 2., 3.])
        y = np.array([1., 2., 4.])
        self.assertRaises(AssertionError, self.assertArraysEqual, x, y)

    def test_ArraysEqual_withEqualMaskedArrays(self):
        # x and y differ in the point where they are masked
        x = ma.array([1., 2., 3.], mask=[True,False,False])
        y = ma.array([7., 2., 3.], mask=[True,False,False])
        self.assertArraysEqual(x,y)
                
    def test_ArraysEqual_withMaskedArraysDifferentMasks(self):
        x = ma.array([1., 2., 3.], mask=[True,False,False])
        y = ma.array([1., 2., 3.], mask=[False,True,False])
        self.assertRaises(AssertionError, self.assertArraysEqual, x, y)

    def test_ArraysEqual_withOneMaskedOneUnmaskedEqual(self):
        # masked array with mask all False is equal to standard numpy array
        x = ma.array([1., 2., 3.], mask=[False,False,False])
        y = np.array([1., 2., 3.])
        self.assertArraysEqual(x,y)

    def test_ArraysEqual_withOneMaskedOneUnmaskedDiffer(self):
        x = ma.array([1., 2., 3.], mask=[True,False,False])
        y = np.array([1., 2., 3.])
        self.assertRaises(AssertionError, self.assertArraysEqual, x, y)
        
if __name__ == '__main__':
    unittest.main()
    
