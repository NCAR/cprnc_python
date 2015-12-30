# Wrapper for scipy.io.netcdf, providing a common interface

from scipy.io.netcdf import netcdf_file
from netcdf_utils import apply_fillvalue

class netcdf_scipy_adapter:
    def __init__(self, filename, mode='r'):
        self._file = netcdf_file(filename, mode)
        self._filename = filename

    def get_varlist(self):
        """Returns a list of variables in the netcdf file"""
        return self._file.variables.keys()

    def get_varlist_bydim(self, dimname):
        """Generator that yields a tuple (varname, index).

        Each variable in the file is returned at least once. For variables that
        have a dimension given by dimname, there is a separate return for each
        index of that dimension. For variables that do not have the given
        dimension, the index will be None.

        For example, if a file contains:
        foo1(dim1, dim2)
        foo2(dim1)
        foo3(dim1, dim2)
        foo4(dim1)
        where dim2 is size 3

        and get_varlist_bydim is called with dimname = 'dim2', then it will
        yield:
        ('foo2', None)
        ('foo4', None)
        ('foo1', 0)
        ('foo3', 0)
        ('foo1', 1)
        ('foo3', 1)
        ('foo1', 2)
        ('foo3', 2)
        """

        dimsize = self.get_dimsize(dimname)

        # First yield variables that do not have the given dimension
        for varname in self.get_varlist():
            var = self._file.variables[varname]
            dimnum = self._get_dimnum(var, dimname)
            if dimnum is None:
                yield (varname, None)

        # Now yield variables with the given dimension
        for index in range(dimsize):
            for varname in self.get_varlist():
                var = self._file.variables[varname]
                dimnum = self._get_dimnum(var, dimname)
                if dimnum is not None:
                    yield (varname, index)
        
    def get_vardata(self, varname, dim_indices={}):
        """Get data corresponding to the given variable name, as a numpy (or
        numpy.ma) array.

        If dim_indices is given, it should be a dictionary whose keys are names of
        dimensions and whose values are the index to use for that dimension.

        For example, if we have a variable foo(lat,lon,time), and dim_indices =
        {'lat':3, 'time':0}, then get_vardata will return an array that contains
        foo[3,:,0].
        """
        var = self._file.variables[varname]

        dim_slices = []
        for dim in var.dimensions:
            if (dim in dim_indices):
                this_slice = dim_indices[dim]
            else:
                this_slice = slice(None)
            dim_slices.append(this_slice)

        vardata = var[dim_slices].copy()

        # NOTE(wjs, 2015-12-23) We do our own application of the mask, rather
        # than relying on the maskandscale argument to netcdf_file, for two
        # reasons: (1) maskandscale was added very recently, and is not yet
        # supported in any scipy release, (2) the application of the mask using
        # the maskandscale option is not ideal - for example, it allows for
        # small differences from the given _FillValue, rather than requiring an
        # exact match.
        vardata_filled = apply_fillvalue(vardata, var._attributes)
        return vardata_filled

    def get_filename(self):
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
        # size of None there. So instead, finda variable with this dimension,
        # and look at its size.
        for varname in self.get_varlist():
            var = self._file.variables[varname]
            dimnum = self._get_dimnum(var, dimname)
            if dimnum is not None:
                dimsize = var.shape[dimnum]
                break
        else:
            dimsize = 0

        return dimsize

    @staticmethod
    def _get_dimnum(var, dimname):
        """Get the dimension number of the given dimension in this variable.

        If this dimension is not present, returns None.

        Arguments:
        var: netcdf_variable object
        dimname: name of dimension of interest
        """

        try:
            dimnum = var.dimensions.index(dimname)
        except ValueError:
            dimnum = None

        return dimnum
