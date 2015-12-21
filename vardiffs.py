from __future__ import print_function

import numpy as np
import numpy.ma as ma

class VarDiffs:
    def __init__(self, var_control, var_test):
        self._compute_stats(var_control, var_test)
        
    def vars_differ(self):
        return self._vars_differ

    def masks_differ(self):
        return self._masks_differ
    
    def _compute_stats(self, var_control, var_test):
        self._compute_vars_differ(var_control, var_test)
        self._compute_masks_differ(var_control, var_test)
        
    def _compute_vars_differ(self, var_control, var_test):
        if (ma.allequal(var_control, var_test)):
            self._vars_differ = False
        else:
            self._vars_differ = True

    def _compute_masks_differ(self, var_control, var_test):
        if (np.array_equal(
            ma.getmaskarray(var_control),
            ma.getmaskarray(var_test))):
            self._masks_differ = False
        else:
            self._masks_differ = True

            
    
