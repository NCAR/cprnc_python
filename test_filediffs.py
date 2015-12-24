#!/usr/bin/env python

from __future__ import print_function

import unittest
from filediffs import FileDiffs
from netcdf_fake import netcdf_fake
import numpy as np
import numpy.ma as ma

class TestFilediffs(unittest.TestCase):

    FILENAME1 = 'foo1.nc'
    FILENAME2 = 'foo2.nc'

    # ------------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------------

    def create_filediffs_with0Vars(self):
        """Create a filediffs object where both files have 0 vars"""
        file1 = netcdf_fake(self.FILENAME1)
        file2 = netcdf_fake(self.FILENAME2)
        return FileDiffs(file1, file2)
        

    # ------------------------------------------------------------------------
    # Tests of num_vars_differ
    # ------------------------------------------------------------------------

    def test_numVarsDiffer_with0Vars(self):
        mydiffs = self.create_filediffs_with0Vars()
        self.assertEqual(mydiffs.num_vars_differ(), 0)

    def test_numVarsDiffer_with3Vars(self):
        file1 = netcdf_fake(
            self.FILENAME1,
            variables = {'var1': np.array([1,2,3]),
                         'var2': np.array([4,5,6]),
                         'var3': np.array([7,8,9])})
        file2 = netcdf_fake(
            self.FILENAME2,
            variables = {'var1': np.array([99,2,3]),  # differs
                         'var2': np.array([4,5,6]),   # same
                         'var3': np.array([99,8,9])}) # differs

        mydiffs = FileDiffs(file1, file2)
        self.assertEqual(mydiffs.num_vars_differ(), 2)

