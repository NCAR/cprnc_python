# Import an available netcdf module

# Typical usage:
# from mynetcdf import netcdf

# TODO(wjs, 2015-12-23) Provide a mechanism to specify a preferred netcdf module
# (or even a list of preferences, in order), rather than having a hard-coded
# ordering in which we try alternative modules

try:
    from netcdf_scipy_adapter import netcdf
except ImportError:
    try:
        from netcdf4_adapter import netcdf
    except ImportError:
        raise ImportError("No netcdf module found")
    
