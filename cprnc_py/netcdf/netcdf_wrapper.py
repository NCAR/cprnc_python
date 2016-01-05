"""Wraps the netcdf import so that the underlying netcdf library can be changed
without needing to change any client code.

Typical usage:
from cprnc_py.netcdf.netcdf_wrapper import netcdf

This 'netcdf' symbol is then a subclass of NetcdfFile (defined in
netcdf_file.py) (client code should not care *which* subclass it is).
"""

from cprnc_py.netcdf.netcdf_file_scipy import NetcdfFileScipy as netcdf
# from cprnc_py.netcdf.netcdf_file_netcdf4 import NetcdfFileNetcdf4 as netcdf
