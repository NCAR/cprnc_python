import numpy as np
import numpy.ma as ma

class NumpyAssertions:
    """This class provides custom assertions on numpy arrays"""

    def assertArraysEqual(self, arr1, arr2):
        masks_equal = np.array_equal(
            ma.getmaskarray(arr1),
            ma.getmaskarray(arr2))
        vals_equal = ma.allequal(arr1, arr2)
        if (not masks_equal):
            raise AssertionError("Masks differ")
        if (not vals_equal):
            raise AssertionError("Values differ")

