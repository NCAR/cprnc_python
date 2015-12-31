# Wrapper for scipy.io.netcdf, providing a common interface

from scipy.io.netcdf import netcdf_file as scipy_netcdf_file
from netcdf_file import NetcdfFile
from netcdf_variable_scipy import NetcdfVariableScipy

class NetcdfFileScipy(NetcdfFile):
    def __init__(self, filename, mode='r'):
        super(NetcdfFileScipy, self).__init__()
        self._file = scipy_netcdf_file(filename, mode)
        self._filename = filename

    def get_varlist(self):
        """Returns a list of variables in the netcdf file"""
        return self._file.variables.keys()

    def get_filename(self):
        """Returns the file name corresponding to this netcdf file"""
        return self._filename

    def get_global_attributes(self):
        """Returns a dictionary of global attributes"""
        
        # I don't like accessing the private _attributes variable, but I don't
        # see any other way to do this
        return self._file._attributes

    def get_dimsize(self, dimname):
        """Returns the size of the given dimension.

        If no variables contain this dimension (even if this dimension is
        defined on the file!), returns 0.
        """

        # To get the size of the given dimension, we cannot simply look at the
        # value in self._file.dimensions, because unlimited dimensions have a
        # size of None there. So instead, find a variable with this dimension,
        # and look at its size. (Note that this is inefficient!)
        return self._get_dimsize_from_variables(dimname)

    def _get_variable(self, varname):
        """Returns a NetcdfVariable-like object for the given variable"""

        return NetcdfVariableScipy(self._file.variables[varname])

