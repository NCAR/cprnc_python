from __future__ import print_function
from cprnc_py.vardiffs import (VarDiffs, VarDiffsNonNumeric)

class FileDiffs(object):
    """This class computes statistics about the differences between two netcdf
    files. This provides the main, high-level functionality of cprnc. It can be
    used by the cprnc command-line tool, or directly by other python code.

    Typical usage is:

    (1) Create a FileDiffs object:
        mydiffs = FileDiffs(file1, file2)

    (2a) (Optionally) Query whether the files differ:
         mydiffs.files_differ()

    (2b) (Optionally) Query specific differences: e.g., how many variables
         differ in various ways:
         - mydiffs.num_vars()
         - mydiffs.num_vars_differ()
         - mydiffs.num_masks_differ()
         - mydiffs.num_dims_differ()
         - mydiffs.num_could_not_be_analyzed()

    (2c) (Optionally) Print statistics on differences:
         str(mydiffs)
    """

    # ------------------------------------------------------------------------
    # Constructor and other special methods
    # ------------------------------------------------------------------------

    def __init__(self, file1, file2, separate_dim="time"):
        """Create a FileDiffs object.

        Arguments:
        file1: netcdf file object with methods get_varlist, get_vardata, etc.
        file2: netcdf file object
        separate_dim: name of dimension to separate along
            If not None or "", then for variables containing the given dimension,
            analysis is done separately for each slice along this dimension
        """

        self._file1 = file1
        self._file2 = file2

        self._vardiffs_list = []
        if separate_dim:
            self._add_vardiffs_separated_by_dim(separate_dim)
        else:
            self._add_vardiffs()

    def __str__(self):
        mystr = ""
        # FIXME(wjs, 2015-12-26) Add some header text

        for var in self._vardiffs_list:
            mystr = mystr + str(var) + "\n\n"

        mystr = mystr + "*" * 132 + "\n\n"
        mystr = mystr + "SUMMARY of cprnc:\n"
        # FIXME(wjs, 2015-12-26) is it right to include the
        # could-not-be-analyzed fields in the 'total number' count? (If not,
        # consider wording the print of the could not be analyzed number
        # differently, too):
        mystr = mystr + " A total number of {0:6d} fields were compared\n".format(
            self.num_vars())
        mystr = mystr + "          of which {0:6d} had non-zero differences\n".format(
            self.num_vars_differ())
        mystr = mystr + "               and {0:6d} had differences in fill patterns\n".format(
            self.num_masks_differ())
        mystr = mystr + "               and {0:6d} had differences in dimension sizes\n".format(
            self.num_dims_differ())
        mystr = mystr + "               and {0:6d} could not be analyzed (e.g., strings)\n".format(
            self.num_could_not_be_analyzed())
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

    def num_vars(self):
        """Returns a count of the total number of variables."""

        return len(self._vardiffs_list)

    def num_vars_differ(self):
        """Returns a count of the number of variables with elements that
        differ."""

        return sum([var.var_diffs.vars_differ() for var in self._vardiffs_list])

    def num_masks_differ(self):
        """Returns a count of the number of variables with masks that differ."""

        return sum([var.var_diffs.masks_differ() for var in self._vardiffs_list])

    def num_dims_differ(self):
        """Returns a count of the number of variables with dims that differ."""

        return sum([var.var_diffs.dims_differ() for var in self._vardiffs_list])

    def num_could_not_be_analyzed(self):
        """Returns a count of the number of variables that could not be
        analyzed."""

        return sum([var.var_diffs.could_not_be_analyzed() for var in self._vardiffs_list])

    def files_differ(self):
        """Returns a boolean variable saying whether the two files differ in any
        meaningful way."""

        if (self.num_vars_differ() > 0 or
            self.num_masks_differ() > 0 or
            self.num_dims_differ() > 0):
            differ = True
        elif (self.num_vars() - self.num_could_not_be_analyzed()) == 0:
            # If no variables could be analyzed, treat this as files differing
            differ = True
        else:
            differ = False
        return differ

    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _add_vardiffs(self):
        """Add all of the vardiffs to self.

        Assumes that self._file1 and self._file2 have already been set.
        """

        for varname in sorted(self._file1.get_varlist()):
            self._add_one_vardiffs((varname, None))

    def _add_vardiffs_separated_by_dim(self, dimname):
        """Add all of the vardiffs to self.

        For variables containing the given dimension, analysis is done
        separately for each slice along this dimension.

        Assumes that self._file1 and self._file2 have already been set.
        """

        for (varname, index) in self._file1.get_varlist_bydim(dimname):
            self._add_one_vardiffs((varname, index), dimname)

    def _add_one_vardiffs(self, varname_index, dimname=None):
        """Add one _DiffWrapper object to the list.

        Arguments:
        varname_index: tuple (varname, index)
        dimname: dimension name (or None)
        """

        (varname, index) = varname_index

        if index is None:
            var_diffs = self._create_vardiffs(varname)
            diff_wrapper = _DiffWrapper.no_slicing(var_diffs, varname)
        else:
            # For now, assume that we want the same index in file2 as in file1.
            #
            # TODO(wjs, 2015-12-31) (optional) allow for different indices,
            # based on reading the associated coordinate variable and finding
            # the matching coordinate (e.g., matching time).
            var_diffs = self._create_vardiffs(varname, {dimname:index})
            diff_wrapper = _DiffWrapper.dim_sliced(var_diffs, varname,
                                                   dimname, index, index)

        self._vardiffs_list.append(diff_wrapper)

    def _create_vardiffs(self, varname, dim_indices={}):
        """Create and return a VarDiffs object.

        Arguments:
        varname: variable name
        dim_indices: dictionary of (dimname:index) pairs giving dimension index or
            indices to use for slicing the data (should agree with index_info)
        """

        # FIXME(wjs, 2015-12-24) Add handling of var not in file2 (maybe add
        # a has_variable method to the netcdf class to help with this;
        # otherwise, could just let it throw an exception)

        if (self._file1.is_var_numeric(varname) and self._file2.is_var_numeric(varname)):
            my_vardiffs = VarDiffs(
                varname,
                self._file1.get_vardata(varname, dim_indices),
                self._file2.get_vardata(varname, dim_indices))
        else:
            my_vardiffs = VarDiffsNonNumeric(varname)

        return my_vardiffs

class _DiffWrapper(object):
    """This class is used by FileDiffs to wrap instances of VarDiffs objects. It
    should not be used by outside code.

    In addition to the VarDiffs objects themselves, this also stores metadata
    about the given differece (variable name, indices used for slicing).

    Typically, instances should be created using one of:
    my_vardiffs = _DiffWrapper.no_slicing(var_diffs, varname)
    my_vardiffs = _DiffWrapper.dim_sliced(var_diffs, varname, separate_dim, index1, index2)
    """

    def __init__(self, var_diffs, varname, separate_dim, index1, index2):
        self.var_diffs = var_diffs
        self.varname = varname
        self.separate_dim = separate_dim
        self.index1 = index1
        self.index2 = index2

    @classmethod
    def no_slicing(cls, var_diffs, varname):
        """Returns a _DiffWrapper object that is appropriate when no slicing was
        done.

        Arguments:
        var_diffs: VarDiffs object
        varname: string: name of this variable
        """

        return cls(var_diffs, varname, separate_dim=None, index1=None, index2=None)

    @classmethod
    def dim_sliced(cls, var_diffs, varname, separate_dim, index1, index2):
        """Returns a _DiffWrapper object that is appropriate when slicing was
        done along one dimension.

        Arguments:
        var_diffs: VarDiffs object
        varname: string: name of this variable
        separate_dim: string: name of dimension that was sliced
        index1: integer: index used in var1
        index2: integer: index used in var2
        """

        return cls(var_diffs, varname, separate_dim, index1, index2)

    def __str__(self):
        mystr = self.varname + "  "
        if self.separate_dim is None:
            pass
        elif self.index1 is None and self.index2 is None:
            pass
        else:
            if self.index1 is None:
                index1_str = "   All"
            else:
                index1_str = "{:6d}".format(self.index1 + 1)
            if self.index2 is None:
                index2_str = "   All"
            else:
                index2_str = "{:6d}".format(self.index2 + 1)

            mystr = mystr + "{dimname} index: {index1} {index2}".format(
                dimname=self.separate_dim, index1=index1_str, index2=index2_str)

        mystr = mystr + "\n"
        mystr = mystr + str(self.var_diffs)
        return mystr
