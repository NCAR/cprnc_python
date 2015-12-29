from __future__ import print_function

import numpy as np
import numpy.ma as ma
from print_utils import index_str

class VarInfo:
    """This class computes and prints a variety of statistics about a single
    variable."""

    # ------------------------------------------------------------------------
    # Constructor and other special methods
    # ------------------------------------------------------------------------

    def __init__(self, varname, var):
        """Create a VarInfo object.

        Arguments:
        varname: string
        var: numpy or numpy.ma array"""

        self._varname = varname

        # Compute all necessary statistics in initialization, so that we don't
        # have to hold onto the variable in memory for later use (in case the
        # variable consumes a lot of memory).
        if not ma.isMA(var):
            var = ma.array(var)
        self._compute_stats(var)

    def __str__(self):
        mystr = "{:8d} {:8d} ".format(self._num_elements, self._num_valid)
        mystr += "{:23.15e} {} ".format(self._max_val, index_str(self._max_indices))
        mystr += "{:23.15e} {} ".format(self._min_val, index_str(self._min_indices))
        mystr += "{:23.15e}\n".format(self._mean_absval)

        return mystr

    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _compute_stats(self, var):
        """Compute and store various statistics for later printing.

        Arguments:
        var: numpy.ma array"""

        self._shape = var.shape
        self._num_elements = var.size
        self._num_valid = var.count()
        if (self._num_valid > 0):
            self._max_val = var.max()
            self._max_loc = var.argmax()
            self._min_val = var.min()
            self._min_loc = var.argmin()
            self._mean_absval = (ma.fabs(var)).mean()
            # Workaround for https://github.com/numpy/numpy/issues/5769
            if (type(self._mean_absval) is np.ma.MaskedArray):
                self._mean_absval = np.float64(self._mean_absval)
        else:
            self._max_val = 0
            self._max_loc = 0
            self._min_val = 0
            self._min_loc = 0
            self._mean_absval = 0

        self._max_indices = np.unravel_index(self._max_loc, var.shape)
        self._min_indices = np.unravel_index(self._min_loc, var.shape)

