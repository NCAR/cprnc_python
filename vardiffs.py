from __future__ import print_function

import numpy as np
import numpy.ma as ma

class VarDiffs:
    """This class holds a variety of statistics about the differences between
    two variables."""

    # ------------------------------------------------------------------------
    # Constructor and other special methods
    # ------------------------------------------------------------------------

    def __init__(self, varname, var1, var2):
        """Create a VarDiffs object.

        Arguments:
        varname: string
        var1: numpy array
        var2: numpy array"""
        
        self._varname = varname

        # Compute all necessary statistics in initialization, so that we don't
        # have to hold onto the variables in memory for later use (in case the
        # variables consume a lot of memory).
        self._compute_stats(var1, var2)

    def __str__(self):
        mystr = ""
        if self.vars_differ():
            mystr = mystr + \
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

        if (self._vars_differ):
            self._rmse = self._compute_rmse(var1, var2)
            # fixme: change the following
            self._normalized_rmse = self._rmse / 2
        else:
            self._rmse = 0.
            self._normalized_rmse = 0.

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
        return np.sqrt(((var1 - var2) ** 2).mean())

            
    
