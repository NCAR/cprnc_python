from cprnc_py.netcdf.netcdf_variable import NetcdfVariable
from cprnc_py.netcdf.netcdf_utils import apply_fillvalue

class NetcdfVariableScipy(NetcdfVariable):
    """Adapter for the scipy netcdf_variable class, making it adapt to a common
    interface."""

    def __init__(self, var):
        """Create a NetcdfVariableScipy instance.

        Arguments:
        var: instance of a scipy netcdf_variable
        """

        super(NetcdfVariableScipy, self).__init__()
        self._var = var

    def get_dimensions(self):
        """Return a list of dimension names"""

        return self._var.dimensions

    def get_shape(self):
        """Return a tuple describing the variable's shape"""

        return self._var.shape

    def get_attributes(self):
        """Return a dictionary of variable attributes on the file"""

        return self._var._attributes

    def _get_data_from_slices(self, dim_slices):
        """Get this variable's data as a numpy array.

        dim_slices: list of slice objects or integer indices; length of
        dim_slices should match the dimensionality of this variable
        """

        # FIXME(wjs, 2015-12-31) Will this work on scalar data?
        vardata = self._var[dim_slices].copy()
        # NOTE(wjs, 2015-12-23) We do our own application of the mask, rather
        # than relying on the maskandscale argument to netcdf_file, for two
        # reasons: (1) maskandscale was added very recently, and is not yet
        # supported in any scipy release, (2) the application of the mask using
        # the maskandscale option is not ideal - for example, it allows for
        # small differences from the given _FillValue, rather than requiring an
        # exact match.
        vardata_filled = apply_fillvalue(vardata, self.get_attributes())

        return vardata_filled

