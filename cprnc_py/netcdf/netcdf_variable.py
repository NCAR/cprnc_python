class NetcdfVariable(object):
    """Base class providing operations that can be performed on a netcdf
    variable.

    This should not be instantiated directly. Instead. instantiate one of its
    subclasses, which provide support for particular python netcdf packages.

    This class serves two purposes:

    (1) Provides a common API through which any python netCDF package can be
    used; this includes:

    - get_dimensions(): Returns a list of dimension names

    - get_shape(): Returns a tuple describing the variable's shape

    - get_attributes(): Returns a dictionary of variable attributes on the file

    - is_numeric(): Returns True if this variable is numeric

    (2) Provides some higher-level methods on top of these netCDF packages, such
    as getting variable data sliced by one or more named dimensions; this
    includes:

    - get_dimnum(dimname): Get the dimension number of the given dimension in
      this variable

    - get_data(dim_indices): Returns the variable's data, possibly sliced along
      one or more named dimensions
    """

    # ------------------------------------------------------------------------
    # Public methods implemented here
    # ------------------------------------------------------------------------

    def get_dimnum(self, dimname):
        """Get the dimension number of the given dimension in this variable.

        If this dimension is not present, returns None.

        Arguments:
        var: NetcdfVariable object
        dimname: name of dimension of interest
        """

        try:
            dimnum = self.get_dimensions().index(dimname)
        except ValueError:
            dimnum = None

        return dimnum

    def get_data(self, dim_indices={}):
        """Get this variable's data as a numpy (or numpy.ma) array.

        If dim_indices is given, it should be a dictionary whose keys are names of
        dimensions and whose values are the index to use for that dimension.

        For example, if we have a variable foo(lat,lon,time), and dim_indices =
        {'lat':3, 'time':0}, then get_data will return an array that contains
        foo[3,:,0].

        A dim_indices value of None means to ignore that entry, thus returning
        all slices for that dimension. e.g., if we have a variable
        foo(lat,lon,time), and dim_indices = {'lat':3, 'time':None}, then
        get_data will return an array that contains foo[3,:,:].
        """

        dim_slices = []
        for dim in self.get_dimensions():
            if (dim in dim_indices):
                dim_index = dim_indices[dim]
                if dim_index is None:
                    this_slice = slice(None)
                else:
                    this_slice = dim_index
            else:
                this_slice = slice(None)
            dim_slices.append(this_slice)
        return self._get_data_from_slices(dim_slices)

    # ------------------------------------------------------------------------
    # Public methods that should be implemented by subclasses
    # ------------------------------------------------------------------------

    def get_dimensions(self):
        """Returns a list of dimension names"""
        raise NotImplementedError

    def get_shape(self):
        """Returns a tuple describing the variable's shape"""
        raise NotImplementedError

    def get_attributes(self):
        """Returns a dictionary of variable attributes on the file"""
        raise NotImplementedError

    def is_numeric(self):
        """Returns True if this variable is numeric, False otherwise (e.g., for characters)"""
        raise NotImplementedError

    # ------------------------------------------------------------------------
    # Private methods that should be implemented by subclasses
    # ------------------------------------------------------------------------

    def _get_data_from_slices(self, dim_slices):
        """Get this variable's data as a numpy array.

        dim_slices: list of slice objects or integer indices; length of
        dim_slices should match the dimensionality of this variable
        """
        raise NotImplementedError
