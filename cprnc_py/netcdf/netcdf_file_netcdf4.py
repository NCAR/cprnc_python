# Wrapper for netCDF4, providing a common interface

from netCDF4 import Dataset
from cprnc_py.netcdf.netcdf_file import NetcdfFile
from cprnc_py.netcdf.netcdf_variable_netcdf4 import NetcdfVariableNetcdf4

class NetcdfFileNetcdf4(NetcdfFile):
    def __init__(self, filename, mode='r'):
        super(NetcdfFileNetcdf4, self).__init__()
        self._file = Dataset(filename, mode)
        self._filename = filename

    def get_varlist(self):
        """Returns a list of variables in the netcdf file"""
        return self._file.variables.keys()

    def get_filename(self):
        """Returns the file name corresponding to this netcdf file"""
        return self._filename

    def get_global_attributes(self):
        """Returns a dictionary of global attributes"""
        
        raise NotImplementedError

    def get_dimsize(self, dimname):
        """Returns the size of the given dimension.

        If this dimension doesn't exist, returns 0.
        """

        try:
            dimsize = len(self._file.dimensions[dimname])
        except KeyError:
            dimsize = 0
        return dimsize

    def _get_variable(self, varname):
        """Returns a NetcdfVariable-like object for the given variable"""

        return NetcdfVariableNetcdf4(self._file.variables[varname])

