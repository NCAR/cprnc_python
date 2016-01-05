from __future__ import print_function

import numpy as np
import numpy.ma as ma
from cprnc_py.numpy_utils import compress_two_arrays
from cprnc_py.varinfo import VarInfo

class VarDiffs(object):
    """This class holds a variety of statistics about the differences between
    two variables.

    This is the main version of the VarDiffs class, which is used for numeric
    variables.

    Typical usage is:

    (1) Create a VarDiffs object:
        mydiff = VarDiffs(varname, var1, var2)

    (2a) (Optionally) Print statistics on differences:
         str(mydiff)

    (2b) (Optionally) Query specific differences:
         - mydiff.vars_differ()
         - mydiff.masks_differ()
         - mydiff.dims_differ()
         - mydiff.could_not_be_analyzed()
    """

    # ------------------------------------------------------------------------
    # Constructor and other special methods
    # ------------------------------------------------------------------------

    def __init__(self, varname, var1, var2):
        """Create a VarDiffs object.

        Arguments:
        varname: string (just used for printing)
        var1, var2: numpy or numpy.ma arrays
        """

        self._varname = varname
        self._var1info = VarInfo(var1)
        self._var2info = VarInfo(var2)

        # Compute all necessary statistics in initialization, so that we don't
        # have to hold onto the variables in memory for later use (in case the
        # variables consume a lot of memory).
        self._compute_stats(var1, var2)

    def __str__(self):
        mystr = ""
        mystr += str(self._var1info)
        mystr += str(self._var2info)
        if self.vars_differ():
            mystr += \
              "RMS {varname:<32}{rms:11.4E}".format(varname=self._varname, rms=self._rmse) + \
              " " * 11 + \
              "NORMALIZED {normalized:11.4E}".format(normalized=self._normalized_rmse)
            
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

    def could_not_be_analyzed(self):
        """Return True if the variables could not be analyzed"""

        return False
    
    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _compute_stats(self, var1, var2):
        self._dims_differ = self._compute_dims_differ(var1, var2)
        if (self.dims_differ()):
            self._vars_differ = False
            self._masks_differ = False
            self._rmse = 0.
            self._normalized_rmse = 0.
        else:
            self._masks_differ = self._compute_masks_differ(var1, var2)

            # For performance reasons, create compressed versions of var1 and var2
            (var1c, var2c) = compress_two_arrays(var1, var2)

            # FIXME(wjs, 2016-01-04) Change the following to use pre-computed
            # abs diff?: check if any abs diff is > 0:
            self._vars_differ = not np.array_equal(var1c, var2c)

            self._rmse = self._compute_rmse(var1c, var2c)
            # FIXME(wjs, 2016-01-03) The following is just a place-holder - we need
            # the true calculation of normalized RMSE
            self._normalized_rmse = self._rmse / 2

    def _compute_dims_differ(self, var1, var2):
        if (var1.shape == var2.shape):
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
        else:
            rmse = 0.
        return rmse

class VarDiffsNonNumeric(object):
    """This version of VarDiffs is used for non-numeric variables.

    Usage is the same as for the standard VarDiffs.
    """

    def __init__(self, varname):
        self._varname = varname

    def __str__(self):
        mystr = "Non-numeric variable could not be analyzed"
        return mystr

    def vars_differ(self):
        return False

    def masks_differ(self):
        return False

    def dims_differ(self):
        return False

    def could_not_be_analyzed(self):
        return True
