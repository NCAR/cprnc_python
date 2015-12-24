# Wrapper for scipy.io.netcdf, providing a common interface

from scipy.io.netcdf import netcdf_file
from netcdf_utils import apply_fillvalue

class netcdf_scipy_adapter:
    def __init__(self, filename, mode='r'):
        self._file = netcdf_file(filename, mode)
        self._filename = filename

    def get_varlist(self):
        """Returns an iterable list of variables in the netcdf file"""
        return self._file.variables.keys()

    def get_vardata(self, varname):
        # NOTE(wjs, 2015-12-23) We do our own application of the mask, rather
        # than relying on the maskandscale argument to netcdf_file, for two
        # reasons: (1) maskandscale was added very recently, and is not yet
        # supported in any scipy release, (2) the application of the mask using
        # the maskandscale option is not ideal - for example, it allows for
        # small differences from the given _FillValue, rather than requiring an
        # exact match.
        var = self._file.variables[varname]
        data = apply_fillvalue(var[:].copy(), var._attributes)
        return data

    def get_filename(self):
        return self._filename

    def get_global_attributes(self):
        """Returns a dictionary of global attributes"""
        
        # I don't like accessing the private _attributes variable, but I don't
        # see any other way to do this
        return self._file._attributes
