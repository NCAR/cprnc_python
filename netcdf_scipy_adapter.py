# Wrapper for scipy.io.netcdf, providing a common interface

from scipy.io.netcdf import netcdf_file
import numpy as np

class netcdf:
    def __init__(self, filename, mode='r'):
        # For now, using mmap = False, because if we let this be true, we get
        # the following warning when a netcdf object is deleted:
        #
        # RuntimeWarning: Cannot close a netcdf_file opened with mmap=True, when
        # netcdf_variables or arrays referring to its data still exist. All data
        # arrays obtained from such files refer directly to data on disk, and
        # must be copied before the file can be cleanly closed. (See netcdf_file
        # docstring for more information on mmap.)
        #
        # I have a feeling this is due to the netcdf object getting garbage
        # collected before the data read from it is garbage collected.
        #
        # An alternative to setting mmap = False may be to make a copy of the
        # data in all cases in get_vardata
        mmap = False

        try:
            self._file = netcdf_file(filename, mode, mmap=mmap, maskandscale=True)
            self._has_maskandscale = True
        except TypeError:
            # For versions of scipy.io.netcdf that do not yet support
            # maskandscale, we need to implement this operation ourselves
            self._file = netcdf_file(filename, mode, mmap=mmap)
            self._has_maskandscale = False

        self._filename = filename

    def get_vardata(self, varname):
        var = self._file.variables[varname]
        # FIXME(wjs, 2015-12-23) Remove the following line
        return var[:]
        if (self._has_maskandscale):
            return var[:]
        else:
            data = var[:].copy()
            data = self._apply_mask(data, var)


    def get_filename(self):
        return self._filename

    def get_global_attributes(self):
        """Returns a dictionary of global attributes"""
        
        # I don't like accessing the private _attributes variable, but I don't
        # see any other way to do this
        return self._file._attributes

    # TODO(wjs, 2015-12-23) Consider moving this to a separate module (e.g.,
    # netcdf_utils): it takes a numpy array and a dictionary of attributes
    # (var._attributes in this case), and does the filling
    @staticmethod
    def _apply_mask(data, var):
        """
        If the given variable has a _FillValue or missing_value attribute, then
        convert the data to a numpy.ma array with the appropriate mask.

        Arguments:
        data: numpy array
        var: netcdf_variable
        """

        missing_value = None
        if '_FillValue' in var._attributes:
            missing_value = var._attributes['_FillValue']
        elif 'missing_value' in var._attributes:
            missing_value = var._attributes['missing_value']

        if missing_value is None:
            return data
        else:
            return np.ma.masked_equal(data, missing_value)
