#!/usr/bin/env python

import unittest
import numpy as np
from cprnc_py.test_utils.custom_assertions import CustomAssertions
from cprnc_py.numpy_utils import compress_two_arrays

class TestNumpyUtils(CustomAssertions):

    # ------------------------------------------------------------------------
    # Tests of compress_two_arrays
    # ------------------------------------------------------------------------

    def test_compressTwoArrays_withUnmaskedArrays(self):
        var1 = np.array([[1,2],[3,4]])
        var2 = np.array([[5,6],[7,8]])
        (var1c, var2c) = compress_two_arrays(var1, var2)
        self.assertArraysEqual(var1c, np.array([1,2,3,4]))
        self.assertArraysEqual(var2c, np.array([5,6,7,8]))

    def test_compressTwoArrays_withUnmaskedMAArrays(self):
        var1 = np.ma.array([[1,2],[3,4]])
        var2 = np.ma.array([[5,6],[7,8]])
        (var1c, var2c) = compress_two_arrays(var1, var2)
        self.assertArraysEqual(var1c, np.array([1,2,3,4]))
        self.assertArraysEqual(var2c, np.array([5,6,7,8]))

    def test_compressTwoArrays_withOneUnmaskedArray(self):
        var1 = np.ma.array([[1,2],[3,4]], mask=[[True,False],[False,True]])
        var2 = np.array([[5,6],[7,8]])
        (var1c, var2c) = compress_two_arrays(var1, var2)
        self.assertArraysEqual(var1c, np.array([2,3]))
        self.assertArraysEqual(var2c, np.array([6,7]))

    def test_compressTwoArrays_withOneUnmaskedMAArray(self):
        var1 = np.ma.array([[1,2],[3,4]], mask=[[True,False],[False,True]])
        var2 = np.ma.array([[5,6],[7,8]])
        (var1c, var2c) = compress_two_arrays(var1, var2)
        self.assertArraysEqual(var1c, np.array([2,3]))
        self.assertArraysEqual(var2c, np.array([6,7]))

    def test_compressTwoArrays_withSameMask(self):
        var1 = np.ma.array([[1,2],[3,4]], mask=[[True,False],[False,True]])
        var2 = np.ma.array([[5,6],[7,8]], mask=[[True,False],[False,True]])
        (var1c, var2c) = compress_two_arrays(var1, var2)
        self.assertArraysEqual(var1c, np.array([2,3]))
        self.assertArraysEqual(var2c, np.array([6,7]))

    def test_compressTwoArrays_withDifferentMasks(self):
        var1 = np.ma.array([[1,2],[3,4]], mask=[[False,False],[False,True]])
        var2 = np.ma.array([[5,6],[7,8]], mask=[[True,False],[False,False]])
        (var1c, var2c) = compress_two_arrays(var1, var2)
        self.assertArraysEqual(var1c, np.array([2,3]))
        self.assertArraysEqual(var2c, np.array([6,7]))

