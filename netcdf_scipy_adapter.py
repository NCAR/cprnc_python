# Wrapper for scipy.io.netcdf, providing a common interface

from scipy.io.netcdf import netcdf_file
import numpy as np

class netcdf:
    def __init__(self, filename, mode='r'):
        self._file = netcdf_file(filename, mode)
        self._filename = filename

    def get_vardata(self, varname):
        # NOTE(wjs, 2015-12-23) We do our own application of the mask, rather
        # than relying on the maskandscale argument to netcdf_file, for two
        # reasons: (1) maskandscale was added very recently, and is not yet
        # supported in any scipy release, (2) the application of the mask using
        # the maskandscale option is not ideal - for example, it allows for
        # small differences from the given _FillValue, rather than requiring an
        # exact match.
        var = self._file.variables[varname]
        data = var[:].copy()
        data = self._apply_mask(data, var._attributes)
        return data

    def get_filename(self):
        return self._filename

    def get_global_attributes(self):
        """Returns a dictionary of global attributes"""
        
        # I don't like accessing the private _attributes variable, but I don't
        # see any other way to do this
        return self._file._attributes

    # TODO(wjs, 2015-12-23) Consider moving this to a separate module (e.g.,
    # netcdf_utils): it takes a numpy array and a dictionary of attributes, and
    # does the filling.
    #
    # One advantage of moving it is that we could unit test it better from
    # elsewhere.
    @staticmethod
    def _apply_mask(data, attributes):
        """
        If the given variable has a _FillValue or missing_value attribute, then
        convert the data to a numpy.ma array with the appropriate mask.

        Arguments:
        data: numpy array
        attributes: dictionary of attributes
        var: netcdf_variable
        """

        missing_value = None
        if '_FillValue' in attributes:
            missing_value = attributes['_FillValue']
        elif 'missing_value' in attributes:
            missing_value = attributes['missing_value']

        if missing_value is None:
            return data
        else:
            return np.ma.masked_equal(data, missing_value)
