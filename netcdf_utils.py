"""This module provides some useful utilities for working with netcdf files."""

import numpy.ma as ma

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

    missing_value = None
    if '_FillValue' in attributes:
        missing_value = attributes['_FillValue']
    elif 'missing_value' in attributes:
        missing_value = attributes['missing_value']

    if missing_value is None:
        return data
    else:
        return ma.masked_equal(data, missing_value)

