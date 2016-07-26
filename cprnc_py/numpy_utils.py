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
    mask_union = np.ma.mask_or(mask1, mask2)
    # TODO(wjs, 2016-01-05) It might be possible to increase the efficiency of
    # the following code slightly by using arr1.compress and arr2.compress on
    # the complement of mask_union, rather than creating two new np.ma
    # arrays. However, then we need to be sure to convert the result back into a
    # numpy array (rather than a numpy.ma array, if it is one). See code in
    # revision 01edb9df04331ef05c7d803907ae4226083b2f49 and prior (but that
    # failed to do the conversion from a numpy.ma array to a numpy array).
    arr1_new = np.ma.masked_where(mask_union, arr1)
    arr2_new = np.ma.masked_where(mask_union, arr2)
    arr1_compressed = arr1_new.compressed()
    arr2_compressed = arr2_new.compressed()
    return (arr1_compressed, arr2_compressed)
