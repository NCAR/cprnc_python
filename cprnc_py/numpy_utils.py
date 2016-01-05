"""Utilities for working with numpy arrays"""

import numpy as np

# ------------------------------------------------------------------------
# Public functions
# ------------------------------------------------------------------------

def compress_two_arrays(arr1, arr2):
    """Given two arrays, possibly masked: Return compressed versions of the
    arrays: 1-d arrays where the only values present are ones that are unmasked
    in both arr1 and arr2.

    Shape of the arrays must be the same.

    Arguments:
    arr1, arr2: numpy or numpy.ma arrays

    Returns a tuple, (arr1_compressed, arr2_compressed).
    """

    mask1 = np.ma.getmask(arr1)
    mask2 = np.ma.getmask(arr2)
    points_to_use = ~np.ma.mask_or(mask1, mask2).ravel()
    if (np.all(points_to_use)):
        # This special case is partly to handle the case where points_to_use is
        # a scalar True value, in which case 'compress' doesn't work
        arr1_compressed = arr1.ravel()
        arr2_compressed = arr2.ravel()
    else:
        arr1_compressed = arr1.compress(points_to_use)
        arr2_compressed = arr2.compress(points_to_use)
    return (arr1_compressed, arr2_compressed)
