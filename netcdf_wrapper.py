"""Wraps the netcdf import so that the underlying netcdf library can be changed
without needing to change any client code.

Typical usage:
from netcdf_wrapper import netcdf
"""

from netcdf_file_scipy import NetcdfFileScipy as netcdf
