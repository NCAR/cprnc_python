from cprnc_py.netcdf.netcdf_variable import NetcdfVariable

class NetcdfVariableFake(NetcdfVariable):
    """Fake replacement for a NetcdfVariable, for the sake of unit testing.

    Attributes are:
    vardata: the data themselves (typically numpy or numpy.ma array)
    dimensions: list of dimension names
    """

    def __init__(self, data, dimnames=None, is_numeric=True):
        """Initialize a netcdf_var_fake instance.

        Arguments:

        data: typically numpy or numpy.ma array
            Must at least support the shape method
        dimnames: list of strings, with one dimname for each dimension in data
            If None, constructs dimnames as dim1, dim2, etc.
        is_numeric: whether this variable is numeric
        """

        super(NetcdfVariableFake, self).__init__()

        self.vardata = data
        ndims = len(data.shape)
        if dimnames is None:
            self.dimensions = ["dim{}".format(i+1) for i in range(ndims)]
        else:
            if (len(dimnames) != ndims):
                raise ValueError("Wrong number of dimnames")
            self.dimensions = dimnames
        self.numeric = is_numeric

    def get_dimensions(self):
        """Return a list of dimension names"""
        return self.dimensions

    def get_shape(self):
        """Return a tuple describing the variable's shape"""
        return self.vardata.shape

    def get_attributes(self):
        """Return a dictionary of variable attributes on the file"""
        return {}

    def is_numeric(self):
        """Return True if this variable is numeric, False otherwise (e.g., for characters)"""
        return self.numeric

    def _get_data_from_slices(self, dim_slices):
        """Get this variable's data as a numpy array.

        dim_slices: list of slice objects or integer indices; length of
        dim_slices should match the dimensionality of this variable
        """
        return self.vardata[dim_slices]
