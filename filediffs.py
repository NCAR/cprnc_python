from __future__ import print_function
from vardiffs import VarDiffs

class FileDiffs:
    """This class computes statistics about the differences between two netcdf
    files."""

    # ------------------------------------------------------------------------
    # Constructor and other special methods
    # ------------------------------------------------------------------------

    def __init__(self, file1, file2):
        """Create a FileDiffs object.

        Arguments:
        file1: netcdf file object with methods get_varlist, get_vardata, etc.
        file2: netcdf file object
        """

        self._file1 = file1
        self._file2 = file2

        self._add_vardiffs()

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def num_vars_differ(self):
        """Return a count of the number of variables with elements that
        differ."""

        return sum([var.vars_differ() for var in self._vardiffs_list])

    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _add_vardiffs(self):
        """Add all of the vardiffs to self.

        Assumes that self._file1 and self._file2 have already been set."""

        self._vardiffs_list = []
        for varname in self._file1.get_varlist():
            # FIXME(wjs, 2015-12-24) Add handling of var not in file2 (maybe add
            # a has_variable method to the netcdf class to help with this;
            # otherwise, could just let it throw an exception)

            # FIXME(wjs, 2015-12-24) Add handling of non-numeric variables

            my_vardiffs = VarDiffs(varname,
                                   self._file1.get_vardata(varname),
                                   self._file2.get_vardata(varname))
            self._vardiffs_list.append(my_vardiffs)
