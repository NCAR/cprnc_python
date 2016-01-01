from __future__ import print_function

import numpy as np
import numpy.ma as ma
from cprnc_py.varinfo import VarInfo

class VarDiffsIndexInfo(object):
    """This class holds information about the slicing done to create a VarDiffs
    object: which dimension was sliced, and what the index of this dimension is
    for var1 and var2.

    Typically, instances should be created using one of:

    myvardiffs = VarDiffsIndexInfo.no_slicing()
    myvardiffs = VarDiffsIndexInfo.dim_sliced(dimname, index1, index2)
    """

    def __init__(self, dimname, index1, index2):
        self._dimname = dimname
        self._index1 = index1
        self._index2 = index2

    def __str__(self):
        if self._dimname is None:
            return ""
        elif self._index1 is None and self._index2 is None:
            return ""
        else:
            if self._index1 is None:
                index1_str = "   All"
            else:
                index1_str = "{:6d}".format(self._index1 + 1)
            if self._index2 is None:
                index2_str = "   All"
            else:
                index2_str = "{:6d}".format(self._index2 + 1)

            return "{dimname} index: {index1} {index2}".format(
                dimname=self._dimname, index1=index1_str, index2=index2_str)

    @classmethod
    def no_slicing(cls):
        """Returns a VarDiffsIndexInfo object that is appropriate when no
        slicing was done."""

        return cls(dimname=None, index1=None, index2=None)

    @classmethod
    def dim_sliced(cls, dimname, index1, index2):
        """Returns a VarDiffsIndexInfo object that is appropriate when slicing
        was done along one dimension.

        Arguments:
        dimname: name of dimension that was sliced
        index1: integer giving the index used in var1
        index2: integer giving the index used in var2
        """

        return cls(dimname, index1, index2)

class VarDiffs(object):
    """This class holds a variety of statistics about the differences between
    two variables."""

    # ------------------------------------------------------------------------
    # Constructor and other special methods
    # ------------------------------------------------------------------------

    def __init__(self, varname, var1, var2, index_info=None):
        """Create a VarDiffs object.

        Arguments:
        varname: string (just used for printing)
        index1, index2: integers giving the index of some dimension of interest:
            var1 and var2 are assumed to be sliced along this dimension (just
            used for printing) (can be None)
        var1, var2: numpy or numpy.ma arrays
        index_info: VarDiffsIndexInfo object (if None, uses VarDiffsIndexInfo.no_slicing())
        """
        
        self._varname = varname
        if index_info is None:
            self._index_info = VarDiffsIndexInfo.no_slicing()
        else:
            self._index_info = index_info

        self._var1info = VarInfo(varname, var1)
        self._var2info = VarInfo(varname, var2)

        # Compute all necessary statistics in initialization, so that we don't
        # have to hold onto the variables in memory for later use (in case the
        # variables consume a lot of memory).
        self._compute_stats(var1, var2)

    def __str__(self):
        mystr = self._varname + "  " + str(self._index_info) + "\n"
        mystr += str(self._var1info)
        mystr += str(self._var2info)
        if self.vars_differ():
            mystr += \
              "RMS {varname:<32}{rms:11.4E}".format(varname=self._varname, rms=self._rmse) + \
              " " * 11 + \
              "NORMALIZED {normalized:11.4E}".format(normalized=self._normalized_rmse) + \
              "\n\n"
            
        return mystr
        


    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def vars_differ(self):
        """Return True if the variables have any elements that differ.

        Only consider points that are unmasked in both variables.
        
        If dimension sizes / shapes differ, return False."""

        return self._vars_differ

    def masks_differ(self):
        """Return True if the variables' masks differ.

        If dimension sizes / shapes differ, return False."""

        return self._masks_differ

    def dims_differ(self):
        """Return True if the variables' dimensions differ in shape or size."""

        return self._dims_differ
    
    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _compute_stats(self, var1, var2):
        self._dims_differ = self._compute_dims_differ(var1, var2)
        if (self.dims_differ()):
            self._vars_differ = False
            self._masks_differ = False
        else:
            self._vars_differ = self._compute_vars_differ(var1, var2)
            self._masks_differ = self._compute_masks_differ(var1, var2)

        self._rmse = self._compute_rmse(var1, var2)
        # fixme: change the following
        self._normalized_rmse = self._rmse / 2

    def _compute_dims_differ(self, var1, var2):
        if (var1.shape == var2.shape):
            return False
        else:
            return True
    
    def _compute_vars_differ(self, var1, var2):
        if (ma.allequal(var1, var2)):
            return False
        else:
            return True

    def _compute_masks_differ(self, var1, var2):
        if (np.array_equal(
            ma.getmaskarray(var1),
            ma.getmaskarray(var2))):
            return False
        else:
            return True

    def _compute_rmse(self, var1, var2):
        """Compute the RMS Error between var1 and var2.

        vars_differ must already be set for self."""

        if (self.vars_differ()):
            rmse = np.sqrt(((var1 - var2) ** 2).mean())
            # Workaround for https://github.com/numpy/numpy/issues/5769
            if type(rmse) is np.ma.MaskedArray:
                rmse = np.float64(rmse)
        else:
            rmse = 0.
        return rmse

            
    
