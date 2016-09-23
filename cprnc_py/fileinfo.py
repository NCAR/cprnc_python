
from __future__ import print_function
from multiprocessing import Pool
from cprnc_py.multiprocessing_fake import PoolFake
from cprnc_py.varinfo import (VarInfo, VarInfoNonNumeric)

class FileInfo(object):
    """This class computes statistics about the variables in a netcdf file.
    This provides the high-level functionality of cprnc_singlefile.
    It can be used by the cprnc_singlefile command-line tool,
    or directly by other python code

    Typical usage is:

    (1 ) Create a FileInfo object:
         - finfo = FileInfo(file)

    (2a) (Optionally) Query statistics about a given variable
         - finfo.var_max(varname)
         - finfo.var_min(varname)
         - finfo.var_average(varname)
         - finfo.var_variance(varname)
         - finfo.var_rms(varname)

    (2b) (Optionally) Print all of the statistics:
         - str(finfo)
    """

    def __init__(self, file, separate_dim="time", nprocs=None):
        """Create a FileInfo object.

        Arguments:
        file: netcdf file object with methods get_varlist, get_vardata, etc.
        separate_dim: name of dimension to separate along
            If not None or "", then for variables containing the given dimension,
            analysis is done separately for each slice along this dimension
        nprocs: Number of tasks to use for the creation of the VarInfo objects
            nprocs = None (the default) means to use a single task, bypassing the
            multiprocessing package.
            nprocs = 1 means to use a single task via the multiprocessing
            package (this adds some overhead, and is just intended for testing)
            nprocs > 1 means to use multiple tasks with the multiprocessing
            package
        """

        
