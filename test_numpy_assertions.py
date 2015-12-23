#!/usr/bin/env python

import unittest
from numpy_assertions import NumpyAssertions
import numpy as np
import numpy.ma as ma

class TestNumpyAssertions(unittest.TestCase):

    def test_ArraysEqual_withEqualArrays(self):
        x = np.array([1., 2., 3.])
        y = np.array([1., 2., 3.])
        sut = NumpyAssertions()
        sut.assertArraysEqual(x,y)
        # Test passes if assertion passes

    def test_ArraysEqual_withDifferentArrays(self):
        x = np.array([1., 2., 3.])
        y = np.array([1., 2., 4.])
        sut = NumpyAssertions()
        self.assertRaises(AssertionError, sut.assertArraysEqual, x, y)

    def test_ArraysEqual_withEqualMaskedArrays(self):
        # x and y differ in the point where they are masked
        x = ma.array([1., 2., 3.], mask=[True,False,False])
        y = ma.array([7., 2., 3.], mask=[True,False,False])
        sut = NumpyAssertions()
        sut.assertArraysEqual(x,y)
                
    def test_ArraysEqual_withMaskedArraysDifferentMasks(self):
        x = ma.array([1., 2., 3.], mask=[True,False,False])
        y = ma.array([1., 2., 3.], mask=[False,True,False])
        sut = NumpyAssertions()
        self.assertRaises(AssertionError, sut.assertArraysEqual, x, y)

    def test_ArraysEqual_withOneMaskedOneUnmaskedEqual(self):
        # masked array with mask all False is equal to standard numpy array
        x = ma.array([1., 2., 3.], mask=[False,False,False])
        y = np.array([1., 2., 3.])
        sut = NumpyAssertions()
        sut.assertArraysEqual(x,y)

    def test_ArraysEqual_withOneMaskedOneUnmaskedDiffer(self):
        x = ma.array([1., 2., 3.], mask=[True,False,False])
        y = np.array([1., 2., 3.])
        sut = NumpyAssertions()
        self.assertRaises(AssertionError, sut.assertArraysEqual, x, y)
        
if __name__ == '__main__':
    unittest.main()
    
