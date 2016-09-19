from __future__ import print_function

import numpy as np
import numpy.ma as ma
import math
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

    def fields_nonshared(self):
        """Return True if the fields are not shared"""

        return False
    
    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _compute_stats(self, var1, var2):
        self._dims_differ = self._compute_dims_differ(var1, var2)
        self._diffs = None
        self._sums = None
        if (self.dims_differ()):
            self._vars_differ = False
            self._masks_differ = False
            self._rmse = 0.
            self._normalized_rmse = 0.
            self._relative_diffs = 0.
        else:
            self._masks_differ = self._compute_masks_differ(var1, var2)

            # For performance reasons, create compressed versions of var1 and var2
            (var1c, var2c) = compress_two_arrays(var1, var2)

            # FIXME(wjs, 2016-01-04) Change the following to use pre-computed
            # abs diff?: check if any abs diff is > 0:
            self._vars_differ = not np.array_equal(var1c, var2c)

            self._rmse = self._compute_rmse(var1c, var2c)
            self._normalized_rmse = self._compute_normalized_rmse(var1c, var2c)
            self._rdiff_max, self._rdiff_maxloc, self._rdiff_logavg = self._compute_rdiff_stats(var1c, var2c)

    def _compute_diffs(self, var1, var2):
        """Computes the differences of var1 and var2

        vars_differ must already be set for self."""
        if self._diffs is None and self.vars_differ():
            # Cache these for multiple uses
            self._diffs = var1 - var2
        return self._diffs

    def _compute_sums(self, var1, var2):
        """Computes the sums of var1 and var2

        vars_differ must already be set for self."""
        if self._sums == None and self.vars_differ():
            # Cache these for multiple uses
            self._sums = var1 + var2
        return self._sums

    def _compute_rdiff_stats(self, var1, var2):
        """Compute the relative difference statistics of var1 and var2.

        vars_differ must already be set for self."""
        if (not self.vars_differ() or len(var1) == 0):
            rdiff_max = np.float('nan')
            rdiff_maxloc = -1
            rdiff_logavg = np.float('nan')
        else:
            maxvals = np.maximum(np.abs(var1), np.abs(var2))
            rdiff = np.abs(self._compute_diffs(var1, var2)) / maxvals
            rdiff_max = np.max(rdiff)
            rdiff_maxloc = np.argmax(rdiff)
            differences = self._compute_diffs(var1, var2) != 0
            numDiffs = np.sum(differences)
            if numDiffs > 0:
                # Compute the sum of logs by taking the products of the logands; +1 if the logand is 0
                # Then take the log of the result
                # Since the log(1) is 0, this does not affect the final sum
                rdiff_prod = np.prod(rdiff[differences])
                if rdiff_prod != np.float('inf') and rdiff_prod > 0.0:
                    rdiff_logsum = -math.log10(rdiff_prod)
                else:
                    # We need to use a different (slower, less accurate) method of computing this,
                    # the product either overflowed or underflowed due to the small exponent
                    rdiff_logs = np.log10(rdiff[differences])
                    rdiff_logsum = -np.sum(rdiff_logs)
                rdiff_logavg = rdiff_logsum / np.sum(differences)
            else:
                rdiff_logavg = np.float('nan')
        return rdiff_max, rdiff_maxloc, rdiff_logavg

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

    def _compute_diffcount(self, var1, var2):
        if (self.vars_differ()):
            diffs = self._compute_diffs(var1, var2)
            diff_count = np.sum(diffs != 0)
        else:
            diff_count = 0
        return diff_count

    def _compute_rmse(self, var1, var2):
        """Compute the RMS Error between var1 and var2.

        vars_differ must already be set for self."""

        if (self.vars_differ()):
            rmse = np.sqrt((self._compute_diffs(var1, var2) ** 2).mean())
        else:
            rmse = 0.
        return rmse

    def _compute_normalized_rmse(self, var1, var2):
        """Compute the normalized RMSE between var1 and var2.

        vars_differ must already be set for self."""
        if (self.vars_differ()):
            norm = (np.average(np.abs(var1)) + np.average(np.abs(var2))) / 2.0
            nrmse = self._compute_rmse(var1, var2) / norm
        else:
            nrmse = 0.
        return nrmse

class VarDiffsNonAnalyzable(object):
    """This version of VarDiffs is used for non-analyzable variables.

    Usage is the same as for the standard Vardiffs.
    """

    def __init__(self, varname):
        self._varname = varname

    def __str__(self):
        raise NotImplementedError("")

    def vars_differ(self):
        return False

    def masks_differ(self):
        return False

    def dims_differ(self):
        return False

    def fields_nonshared(self):
        return False

    def could_not_be_analyzed(self):
        return True

class VarDiffsNonNumeric(VarDiffsNonAnalyzable):
    """This version of VarDiffs is used for non-numeric variables.

    Usage is the same as for the standard VarDiffs.
    """

    def __init__(self, varname):
        super(VarDiffsNonNumeric, self).__init__(varname)

    def __str__(self):
        mystr = "Non-numeric variable could not be analyzed"
        return mystr

class VarDiffsUnsharedVar(VarDiffsNonAnalyzable):
    """This version of VarDiffs is used for non-numeric variables.

    Usage is the same as for the standard VarDiffs.
    """

    def __init__(self, varname):
        super(VarDiffsUnsharedVar, self).__init__(varname)

    def __str__(self):
        mystr = "Unshared variable could not be analyzed"
        return mystr

    def fields_nonshared(self):
        return True
