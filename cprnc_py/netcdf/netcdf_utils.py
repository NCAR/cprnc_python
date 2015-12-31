"""This module provides some useful utilities for working with netcdf files."""

import numpy as np

def apply_fillvalue(data, attributes):
    """Apply the _FillValue or missing_value attribute to the given data array,
    producing a masked array (numpy.ma).

    If both _FillValue and missing_value are given, then _FillValue takes
    precedence.

    If neither _FillValue nor missing_value are given, then the result has no
    mask.

    Arguments:
    data: numpy array
    attributes: dictionary of attributes
    """

    if '_FillValue' in attributes:
        missing_value = attributes['_FillValue']
    elif 'missing_value' in attributes:
        missing_value = attributes['missing_value']
    else:
        missing_value = None

    if missing_value is None:
        newdata = data
    else:
        try:
            missing_value_isnan = np.isnan(missing_value)
        except TypeError:
            # some data types (e.g., characters) cannot be tested for NaN
            missing_value_isnan = False

        if (missing_value_isnan):
            mymask = np.isnan(data)
        else:
            mymask = (data == missing_value)

        newdata = np.ma.masked_where(mymask, data)

    return newdata

