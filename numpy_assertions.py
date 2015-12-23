import numpy as np
import numpy.ma as ma

class NumpyAssertions:
    """This class provides custom assertions on numpy arrays"""

    def assertArraysEqual(self, arr1, arr2):
        mask1 = ma.getmaskarray(arr1)
        mask2 = ma.getmaskarray(arr2)
        masks_equal = np.array_equal(mask1, mask2)
        if (not masks_equal):
            msg = "Masks differ:\n" + \
              str(mask1) + " != " + str(mask2) + "\n" + \
              "Arrays are: \n" + \
              str(arr1) + "\n" + \
              str(arr2)

            raise AssertionError(msg)

        vals_equal = ma.allequal(arr1, arr2)
        if (not vals_equal):
            msg = "Values differ:\n" + \
              str(arr1) + " != " + str(arr2)
            raise AssertionError(msg)

