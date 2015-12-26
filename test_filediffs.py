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
        num_differ = mydiffs.num_vars_differ()
        self.assertEqual(num_differ, 0)

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
        num_differ = mydiffs.num_vars_differ()
        self.assertEqual(num_differ, 2)

    # ------------------------------------------------------------------------
    # Tests of num_masks_differ
    # ------------------------------------------------------------------------

    def test_numMasksDiffer_with3Vars(self):
        file1 = netcdf_fake(
            self.FILENAME1,
            variables = {'var1': ma.array([1,2,3], mask=[True,False,False]),
                         'var2': ma.array([4,5,6], mask=[False,True,False]),
                         'var3': ma.array([7,8,9], mask=[False,False,True])})
        file2 = netcdf_fake(
            self.FILENAME2,
            variables = {'var1': ma.array([1,2,3], mask=[False,True,False]),  # differs
                         'var2': ma.array([4,5,6], mask=[False,True,False]),  # same
                         'var3': ma.array([7,8,9], mask=[False,True,False])}) # differs
        mydiffs = FileDiffs(file1, file2)
        num_differ = mydiffs.num_masks_differ()
        self.assertEqual(num_differ, 2)

    # ------------------------------------------------------------------------
    # Tests of num_dims_differ
    # ------------------------------------------------------------------------

    def test_numDimsDiffer_with3Vars(self):
        file1 = netcdf_fake(
            self.FILENAME1,
            variables = {'var1': np.array([1,2,3]),
                         'var2': np.array([4,5,6]),
                         'var3': np.array([7,8,9])})
        file2 = netcdf_fake(
            self.FILENAME2,
            variables = {'var1': np.array([1,2]),       # differs
                         'var2': np.array([4,5,6]),     # same
                         'var3': np.array([7,8,9,10])}) # differs
        mydiffs = FileDiffs(file1, file2)
        num_differ = mydiffs.num_dims_differ()
        self.assertEqual(num_differ, 2)

    # ------------------------------------------------------------------------
    # Tests of files_differ
    # ------------------------------------------------------------------------

    def test_filesDiffer_withEqualVariables(self):
        file1 = netcdf_fake(
            self.FILENAME1,
            variables = {'var1': np.array([1,2,3])})
        file2 = netcdf_fake(
            self.FILENAME2,
            variables = {'var1': np.array([1,2,3])})
        mydiffs = FileDiffs(file1, file2)
        differ = mydiffs.files_differ()
        self.assertFalse(differ)

    def test_filesDiffer_withVarsDiffer(self):
        file1 = netcdf_fake(
            self.FILENAME1,
            variables = {'var1': np.array([1,2,3])})
        file2 = netcdf_fake(
            self.FILENAME2,
            variables = {'var1': np.array([1,2,4])})
        mydiffs = FileDiffs(file1, file2)
        differ = mydiffs.files_differ()
        self.assertTrue(differ)

    def test_filesDiffer_withMasksDiffer(self):
        file1 = netcdf_fake(
            self.FILENAME1,
            variables = {'var1': ma.array([1,2,3], mask=[True,False,False])})
        file2 = netcdf_fake(
            self.FILENAME2,
            variables = {'var1': ma.array([1,2,3], mask=[False,True,False])})
        mydiffs = FileDiffs(file1, file2)
        differ = mydiffs.files_differ()
        self.assertTrue(differ)

    def test_filesDiffer_withDimsDiffer(self):
        file1 = netcdf_fake(
            self.FILENAME1,
            variables = {'var1': np.array([1,2,3])})
        file2 = netcdf_fake(
            self.FILENAME2,
            variables = {'var1': np.array([1,2])})
        mydiffs = FileDiffs(file1, file2)
        differ = mydiffs.files_differ()
        self.assertTrue(differ)

    # ------------------------------------------------------------------------
    # Tests of __str__
    #
    # Currently we just test the critical piece: the final statement of whether
    # the files are DIFFERENT or IDENTICAL
    # ------------------------------------------------------------------------

    def test_str_differ(self):
        file1 = netcdf_fake(
            self.FILENAME1,
            variables = {'var1': np.array([1,2,3])})
        file2 = netcdf_fake(
            self.FILENAME2,
            variables = {'var1': np.array([1,2,4])})
        mydiffs = FileDiffs(file1, file2)
        mystr = str(mydiffs)
        self.assertRegexpMatches(mystr, "diff_test.*DIFFERENT")
        self.assertNotRegexpMatches(mystr, "diff_test.*IDENTICAL")

    def test_str_identical(self):
        file1 = netcdf_fake(
            self.FILENAME1,
            variables = {'var1': np.array([1,2,3])})
        file2 = netcdf_fake(
            self.FILENAME2,
            variables = {'var1': np.array([1,2,3])})
        mydiffs = FileDiffs(file1, file2)
        mystr = str(mydiffs)
        self.assertRegexpMatches(mystr, "diff_test.*IDENTICAL")
        self.assertNotRegexpMatches(mystr, "diff_test.*DIFFERENT")
