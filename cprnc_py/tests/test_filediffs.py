#!/usr/bin/env python

from __future__ import print_function

import unittest
from cprnc_py.filediffs import FileDiffs
from cprnc_py.netcdf.netcdf_file_fake import NetcdfFileFake
from cprnc_py.netcdf.netcdf_variable_fake import NetcdfVariableFake
from cprnc_py.multiprocessing_fake import PoolFake
import numpy as np
from cprnc_py.test_utils.custom_assertions import CustomAssertions

class TestFilediffs(CustomAssertions):

    FILENAME1 = 'foo1.nc'
    FILENAME2 = 'foo2.nc'

    # ------------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------------

    def create_filediffs_with0Vars(self):
        """Create a filediffs object where both files have 0 vars"""
        file1 = NetcdfFileFake(self.FILENAME1)
        file2 = NetcdfFileFake(self.FILENAME2)
        return self.create_filediffs(file1, file2, separate_dim=None)

    def create_filediffs(self, file1, file2, separate_dim):
        pool = PoolFake()
        return FileDiffs(file1, file2, pool, separate_dim)

    # ------------------------------------------------------------------------
    # Tests of num_vars_differ
    # ------------------------------------------------------------------------

    def test_numVarsDiffer_with0Vars(self):
        mydiffs = self.create_filediffs_with0Vars()
        num_differ = mydiffs.num_vars_differ()
        self.assertEqual(num_differ, 0)

    def test_numVarsDiffer_with3Vars(self):
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,3])),
                         'var2': NetcdfVariableFake(np.array([4,5,6])),
                         'var3': NetcdfVariableFake(np.array([7,8,9]))})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': NetcdfVariableFake(np.array([99,2,3])),  # differs
                         'var2': NetcdfVariableFake(np.array([4,5,6])),   # same
                         'var3': NetcdfVariableFake(np.array([99,8,9]))}) # differs
        mydiffs = self.create_filediffs(file1, file2, separate_dim=None)
        num_differ = mydiffs.num_vars_differ()
        self.assertEqual(num_differ, 2)

    def test_numVarsDiffer_withVariableSeparatedByDim(self):
        # make sure that filediffs separates a variable by some dimension if
        # requested to do so
        data = np.array([[1,2,3],[4,5,6]])
        data_plus_1 = data + 1
        variable = NetcdfVariableFake(data, ('dim1', 'dim2'))
        variable_plus_1 = NetcdfVariableFake(data_plus_1, ('dim1', 'dim2'))
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': variable})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': variable_plus_1})
        mydiffs = self.create_filediffs(file1, file2, separate_dim='dim2')
        num_differ = mydiffs.num_vars_differ()
        self.assertEqual(num_differ, 3)


    def test_numVarsDiffer_withVariableWithoutSeparateDim(self):
        # If we ask to separate on a given dimension, but a given variable
        # doesn't have that dimension, make sure this variable is just counted
        # once
        data = np.array([[1,2,3],[4,5,6]])
        data_plus_1 = data + 1
        variable = NetcdfVariableFake(data, ('dim1', 'dim2'))
        variable_plus_1 = NetcdfVariableFake(data_plus_1, ('dim1', 'dim2'))
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': variable})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': variable_plus_1})
        mydiffs = self.create_filediffs(file1, file2, separate_dim='dim_does_not_exist')
        num_differ = mydiffs.num_vars_differ()
        self.assertEqual(num_differ, 1)

    # ------------------------------------------------------------------------
    # Tests of num_masks_differ
    # ------------------------------------------------------------------------

    def test_numMasksDiffer_with3Vars(self):
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': NetcdfVariableFake(np.ma.array([1,2,3], mask=[True,False,False])),
                         'var2': NetcdfVariableFake(np.ma.array([4,5,6], mask=[False,True,False])),
                         'var3': NetcdfVariableFake(np.ma.array([7,8,9], mask=[False,False,True]))})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': NetcdfVariableFake(np.ma.array([1,2,3], mask=[False,True,False])),  # differs
                         'var2': NetcdfVariableFake(np.ma.array([4,5,6], mask=[False,True,False])),  # same
                         'var3': NetcdfVariableFake(np.ma.array([7,8,9], mask=[False,True,False]))}) # differs
        mydiffs = self.create_filediffs(file1, file2, separate_dim=None)
        num_differ = mydiffs.num_masks_differ()
        self.assertEqual(num_differ, 2)

    # ------------------------------------------------------------------------
    # Tests of num_dims_differ
    # ------------------------------------------------------------------------

    def test_numDimsDiffer_with3Vars(self):
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,3])),
                         'var2': NetcdfVariableFake(np.array([4,5,6])),
                         'var3': NetcdfVariableFake(np.array([7,8,9]))})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': NetcdfVariableFake(np.array([1,2])),       # differs
                         'var2': NetcdfVariableFake(np.array([4,5,6])),     # same
                         'var3': NetcdfVariableFake(np.array([7,8,9,10]))}) # differs
        mydiffs = self.create_filediffs(file1, file2, separate_dim=None)
        num_differ = mydiffs.num_dims_differ()
        self.assertEqual(num_differ, 2)

    def test_numDimsDiffer_withVariable2WithoutSeparateDim(self):
        # If we ask to compare two variables separated by some dimension, where
        # the variable has that dimension in file 1 but not in file 2, we should
        # get N dims_differ, where N is the size of the dimension in file 1
        data = np.array([[1,2,3],[4,5,6]])
        variable1 = NetcdfVariableFake(data, ('dim1', 'dim2'))
        variable2 = NetcdfVariableFake(data, ('dim1', 'dim3'))
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': variable1})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': variable2})
        mydiffs = self.create_filediffs(file1, file2, separate_dim='dim2')
        num_differ = mydiffs.num_dims_differ()
        self.assertEqual(num_differ, 3)

    # ------------------------------------------------------------------------
    # Tests of num_could_not_be_analyzed
    # ------------------------------------------------------------------------

    def test_numCouldNotBeAnalyzed_withCharVariable(self):
        var_numeric = NetcdfVariableFake(np.array([1,2,3]))
        var_char = NetcdfVariableFake(np.array(['a','b','c']), is_numeric=False)
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': var_numeric,
                         'var2': var_char})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': var_numeric,
                         'var2': var_char})
        mydiffs = self.create_filediffs(file1, file2, separate_dim=None)
        num_could_not_be_analyzed = mydiffs.num_could_not_be_analyzed()
        self.assertEqual(num_could_not_be_analyzed, 1)

    # ------------------------------------------------------------------------
    # Tests of files_differ
    # ------------------------------------------------------------------------

    def test_filesDiffer_withEqualVariables(self):
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,3]))})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,3]))})
        mydiffs = self.create_filediffs(file1, file2, separate_dim=None)
        differ = mydiffs.files_differ()
        self.assertFalse(differ)

    def test_filesDiffer_withVarsDiffer(self):
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,3]))})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,4]))})
        mydiffs = self.create_filediffs(file1, file2, separate_dim=None)
        differ = mydiffs.files_differ()
        self.assertTrue(differ)

    def test_filesDiffer_withMasksDiffer(self):
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': NetcdfVariableFake(np.ma.array([1,2,3], mask=[True,False,False]))})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': NetcdfVariableFake(np.ma.array([1,2,3], mask=[False,True,False]))})
        mydiffs = self.create_filediffs(file1, file2, separate_dim=None)
        differ = mydiffs.files_differ()
        self.assertTrue(differ)

    def test_filesDiffer_withDimsDiffer(self):
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,3]))})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': NetcdfVariableFake(np.array([1,2]))})
        mydiffs = self.create_filediffs(file1, file2, separate_dim=None)
        differ = mydiffs.files_differ()
        self.assertTrue(differ)

    def test_filesDiffer_withNoVariables(self):
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {})
        mydiffs = self.create_filediffs(file1, file2, separate_dim=None)
        differ = mydiffs.files_differ()
        self.assertTrue(differ)

    def test_filesDiffer_withNoVarsAnalyzed(self):
        var_char = NetcdfVariableFake(np.array(['a','b','c']), is_numeric=False)
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': var_char})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': var_char})
        mydiffs = self.create_filediffs(file1, file2, separate_dim=None)
        differ = mydiffs.files_differ()
        self.assertTrue(differ)



    # ------------------------------------------------------------------------
    # Tests of __str__
    #
    # Currently we just test the critical piece: the final statement of whether
    # the files are DIFFERENT or IDENTICAL
    # ------------------------------------------------------------------------

    def test_str_differ(self):
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,3]))})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,4]))})
        mydiffs = self.create_filediffs(file1, file2, separate_dim=None)
        mystr = str(mydiffs)
        self.assertRegexMatches(mystr, "diff_test.*DIFFERENT")
        self.assertNotRegexMatches(mystr, "diff_test.*IDENTICAL")

    def test_str_identical(self):
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,3]))})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,3]))})
        mydiffs = self.create_filediffs(file1, file2, separate_dim=None)
        mystr = str(mydiffs)
        self.assertRegexMatches(mystr, "diff_test.*IDENTICAL")
        self.assertNotRegexMatches(mystr, "diff_test.*DIFFERENT")

    def test_str_separateDim(self):
        # Just a smoke test of the printing when separate_dim is given
        file1 = NetcdfFileFake(
            self.FILENAME1,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,3]))})
        file2 = NetcdfFileFake(
            self.FILENAME2,
            variables = {'var1': NetcdfVariableFake(np.array([1,2,4]))})
        mydiffs = self.create_filediffs(file1, file2, separate_dim='dim1')
        mystr = str(mydiffs)

if __name__ == '__main__':
    unittest.main()
