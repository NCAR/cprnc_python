#!/usr/bin/env python

from __future__ import print_function

import unittest
import numpy as np
import numpy.ma as ma
from os.path import (join, dirname)
from cprnc_py.test_utils.custom_assertions import CustomAssertions
from cprnc_py.netcdf.netcdf_file_scipy import NetcdfFileScipy as netcdf

class TestNetcdfFileScipy(CustomAssertions):
    """This class provides tests of NetcdfFileScipy, as well as the
    functionality in its base class (NetcdfFile).

    This also provides test coverage of NetcdfVariableScipy and NetcdfVariable.
    """

    TEST_DATA_PATH = join(dirname(__file__), 'test_inputs')
    TESTFILE_BASIC = join(TEST_DATA_PATH, 'testfile_basic.nc')
    TESTFILE_MULTIPLE_TIMES = join(TEST_DATA_PATH, 'testfile_multipleTimes_someTimeless.nc')
    TESTFILE_CHAR = join(TEST_DATA_PATH, 'testfile_char.nc')

    def test_getDimsize_withBasicData(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        dimsize = mynetcdf.get_dimsize('lat')
        self.assertEqual(dimsize, 5)

    def test_getDimsize_withUnlimitedDimension(self):
        # Make sure we get the dimension size of the unlimited dimension correctly
        mynetcdf = netcdf(self.TESTFILE_MULTIPLE_TIMES)
        dimsize = mynetcdf.get_dimsize('time')
        self.assertEqual(dimsize, 3)

    def test_getDimsize_withNonexistentDimension(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        dimsize = mynetcdf.get_dimsize('nonexistent')
        self.assertEqual(dimsize, 0)

    def test_getVarlist_withBasicData(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        myvars = sorted(mynetcdf.get_varlist())
        self.assertEqual(myvars, ['lat','lon','testvar','testvar2_hasfill','testvar3','time'])

    def test_getVarlistByDim_withMultipleTimesSeparateOnTime(self):
        mynetcdf = netcdf(self.TESTFILE_MULTIPLE_TIMES)
        myvars = mynetcdf.get_varlist_bydim('time')
        self.assertSameItems(
            myvars,
            [('lat',None), ('lon',None), ('testvar_notime',None), ('testvar2_notime',None),
             ('time',0), ('testvar',0), ('testvar2',0),
             ('time',1), ('testvar',1), ('testvar2',1),
             ('time',2), ('testvar',2), ('testvar2',2)])

    def test_getVarlistByDim_withMultipleTimesSeparateOnLon(self):
        mynetcdf = netcdf(self.TESTFILE_MULTIPLE_TIMES)
        myvars = mynetcdf.get_varlist_bydim('lon')
        self.assertSameItems(
            myvars,
            [('lat',None), ('time',None),
             ('lon',0), ('testvar_notime',0), ('testvar2_notime',0),
             ('testvar',0), ('testvar2',0),
             ('lon',1), ('testvar_notime',1), ('testvar2_notime',1),
             ('testvar',1), ('testvar2',1)])

    def test_getVardata_withBasicData(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        mydata = mynetcdf.get_vardata('testvar')
        expected = np.array([[[1.,2.],[3.,4.],[5.,6.],[7.,8.],[9.,10.]]])
        self.assertArraysEqual(mydata, expected)

    def test_getVardata_withFillValue(self):
        IRRELEVANT_VAL = 9999.
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        mydata = mynetcdf.get_vardata('testvar2_hasfill')
        expected = ma.array([[[2.,4.],[6.,8.],[10.,IRRELEVANT_VAL],
                              [14.,16.],[18.,20.]]],
                            mask=[[[False,False],[False,False],[False,True],
                                   [False,False],[False,False]]])
        self.assertArraysEqual(mydata, expected)

    def test_getVardata_withDimSlice(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        mydata = mynetcdf.get_vardata('testvar', {'lon':1})
        expected = np.array([[  2.,   4.,   6.,   8.,  10.]])
        self.assertArraysEqual(mydata, expected)

    def test_getVardata_withDimSliceNone(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        mydata = mynetcdf.get_vardata('testvar', {'lon':None})
        expected = np.array([[[1.,2.],[3.,4.],[5.,6.],[7.,8.],[9.,10.]]])
        self.assertArraysEqual(mydata, expected)

    def test_getVardata_with2DimSlices(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        mydata = mynetcdf.get_vardata('testvar', {'lon':1, 'lat':2})
        expected = np.array([6.])
        self.assertArraysEqual(mydata, expected)

    def test_getFilename(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        self.assertEqual(self.TESTFILE_BASIC, mynetcdf.get_filename())

    def test_getGlobalAttributes(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        myatts = mynetcdf.get_global_attributes()
        expected = {'attribute1':b'foo1', 'attribute2':b'foo2', 'attribute3':b'foo3'}
        self.assertEqual(expected, myatts)

    def test_isVarNumeric_withNumericVar(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        is_numeric = mynetcdf.is_var_numeric('testvar')
        self.assertTrue(is_numeric)

    def test_isVarNumeric_withCharacterVar(self):
        mynetcdf = netcdf(self.TESTFILE_CHAR)
        is_numeric = mynetcdf.is_var_numeric('mystr')
        self.assertFalse(is_numeric)

if __name__ == '__main__':
    unittest.main()
        
