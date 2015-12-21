from __future__ import print_function

import numpy as np
import numpy.ma as ma

class VarDiffs:

    # ------------------------------------------------------------------------
    # Constructor and other special methods
    # ------------------------------------------------------------------------

    def __init__(self, var1, var2):
        self._compute_stats(var1, var2)


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

            
    
