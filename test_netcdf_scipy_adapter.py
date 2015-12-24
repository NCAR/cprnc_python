#!/usr/bin/env python

from __future__ import print_function

import unittest
import numpy as np
import numpy.ma as ma
from numpy_assertions import NumpyAssertions
from netcdf_scipy_adapter import netcdf_scipy_adapter as netcdf

class TestNetcdfScipyAdapter(unittest.TestCase, NumpyAssertions):

    TESTFILE_BASIC = 'test_inputs/testfile_basic.nc'

    def test_getVarlist_withBasicData(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        myvars = sorted(mynetcdf.get_varlist())
        self.assertEqual(myvars, ['lat','lon','testvar','testvar2_hasfill','testvar3','time'])


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
        
    def test_getFilename(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        self.assertEqual(self.TESTFILE_BASIC, mynetcdf.get_filename())

    def test_getGlobalAttributes(self):
        mynetcdf = netcdf(self.TESTFILE_BASIC)
        myatts = mynetcdf.get_global_attributes()
        expected = {'attribute1':'foo1', 'attribute2':'foo2', 'attribute3':'foo3'}
        self.assertEqual(expected, myatts)
    
if __name__ == '__main__':
    unittest.main()
        
