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

    def __str__(self):
        mystr = ""
        # FIXME(wjs, 2015-12-26) Add some header text

        for var in self._vardiffs_list:
            mystr = mystr + str(var)

        mystr = mystr + "*" * 132 + "\n\n"
        mystr = mystr + "SUMMARY of cprnc:\n"
        # FIXME(wjs, 2015-12-26) is it right to include the
        # could-not-be-analyzed fields in the following count?:
        mystr = mystr + " A total number of {0:6d} fields were compared\n".format(
            len(self._vardiffs_list))
        mystr = mystr + "          of which {0:6d} had non-zero differences\n".format(
            self.num_vars_differ())
        mystr = mystr + "               and {0:6d} had differences in fill patterns\n".format(
            self.num_masks_differ())
        mystr = mystr + "               and {0:6d} had differences in dimension sizes\n".format(
            self.num_dims_differ())
        # FIXME(wjs, 2015-12-26) Add count of could-not-be-analyzed
        # FIXME(wjs, 2015-12-26) Add count of fields not found

        mystr = mystr + "  diff_test: the two files seem to be "
        if (self.files_differ()):
            mystr = mystr + "DIFFERENT"
        else:
            mystr = mystr + "IDENTICAL"
        mystr = mystr + "\n\n"

        return mystr

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def num_vars_differ(self):
        """Return a count of the number of variables with elements that
        differ."""

        return sum([var.vars_differ() for var in self._vardiffs_list])

    def num_masks_differ(self):
        """Return a count of the number of variables with masks that differ."""

        return sum([var.masks_differ() for var in self._vardiffs_list])

    def num_dims_differ(self):
        """Return a count of the number of variables with dims that differ."""

        return sum([var.dims_differ() for var in self._vardiffs_list])

    def files_differ(self):
        """Returns a boolean variable saying whether the two files differ in any
        meaningful way."""

        differ = (self.num_vars_differ() > 0 or
                  self.num_masks_differ() > 0 or
                  self.num_dims_differ() > 0)
        return differ

    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _add_vardiffs(self):
        """Add all of the vardiffs to self.

        Assumes that self._file1 and self._file2 have already been set."""

        self._vardiffs_list = []
        for varname in sorted(self._file1.get_varlist()):
            # FIXME(wjs, 2015-12-24) Add handling of var not in file2 (maybe add
            # a has_variable method to the netcdf class to help with this;
            # otherwise, could just let it throw an exception)

            # FIXME(wjs, 2015-12-24) Add handling of non-numeric variables

            my_vardiffs = VarDiffs(varname,
                                   self._file1.get_vardata(varname),
                                   self._file2.get_vardata(varname))
            self._vardiffs_list.append(my_vardiffs)
