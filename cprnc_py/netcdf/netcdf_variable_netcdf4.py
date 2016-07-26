from cprnc_py.netcdf.netcdf_variable import NetcdfVariable
from cprnc_py.netcdf.netcdf_utils import apply_fillvalue
import numpy as np

class NetcdfVariableNetcdf4(NetcdfVariable):
    """Adapter for the Netcdf4 Variable class, making it adapt to a common
    interface."""

    def __init__(self, var):
        """Create a NetcdfVariableNetcdf4 instance.

        Arguments:
        var: instance of a Netcdf4 Variable
        """

        super(NetcdfVariableNetcdf4, self).__init__()
        self._var = var

    def get_dimensions(self):
        """Returns a list of dimension names"""

        return self._var.dimensions

    def get_shape(self):
        """Returns a tuple describing the variable's shape"""

        return self._var.shape

    def get_attributes(self):
        """Returns a dictionary of variable attributes on the file"""

        raise NotImplementedError

    def is_numeric(self):
        """Returns True if this variable is numeric, False otherwise (e.g., for characters)"""

        mytype = self._var.dtype
        if mytype.kind == 'S' or mytype.kind == 'U':
            return False
        else:
            return True

    def _get_data_from_slices(self, dim_slices):
        """Get this variable's data as a numpy array.

        dim_slices: list of slice objects or integer indices; length of
        dim_slices should match the dimensionality of this variable
        """

        # FIXME(wjs, 2016-01-05) Will this work on scalar data?
        vardata = self._var[dim_slices]
        return vardata
