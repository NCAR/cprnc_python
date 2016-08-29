"""
NetCDF reader/writer module.

This module is used to read and create NetCDF files. NetCDF files are
accessed through the `netcdf_file` object. Data written to and from NetCDF
files are contained in `netcdf_variable` objects. Attributes are given
as member variables of the `netcdf_file` and `netcdf_variable` objects.

This module implements the Scientific.IO.NetCDF API to read and create
NetCDF files. The same API is also used in the PyNIO and pynetcdf
modules, allowing these modules to be used interchangeably when working
with NetCDF files.

Only NetCDF3 is supported here; for NetCDF4 see
`netCDF4-python <http://unidata.github.io/netcdf4-python/>`__,
which has a similar API.

"""

from __future__ import division, print_function, absolute_import

# TODO:
# * properly implement ``_FillValue``.
# * fix character variables.
# * implement PAGESIZE for Python 2.6?

# The Scientific.IO.NetCDF API allows attributes to be added directly to
# instances of ``netcdf_file`` and ``netcdf_variable``. To differentiate
# between user-set attributes and instance attributes, user-set attributes
# are automatically stored in the ``_attributes`` attribute by overloading
#``__setattr__``. This is the reason why the code sometimes uses
#``obj.__dict__['key'] = value``, instead of simply ``obj.key = value``;
# otherwise the key would be inserted into userspace attributes.


__all__ = ['netcdf_file']


import warnings
import weakref
from operator import mul
import mmap as mm
import sys
import types
import os

import numpy as np
from numpy.compat import asbytes, asstr
from numpy import fromstring, dtype, empty, array, asarray
from numpy import little_endian as LITTLE_ENDIAN
from functools import reduce

import cprnc_py.netcdf.fs_utils as fs_utils

PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str,
    integer_types = int,
    class_types = type,
    text_type = str
    binary_type = bytes

    MAXSIZE = sys.maxsize
else:
    string_types = basestring,
    integer_types = (int, long)
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str

ABSENT = b'\x00\x00\x00\x00\x00\x00\x00\x00'
ZERO = b'\x00\x00\x00\x00'
NC_BYTE = b'\x00\x00\x00\x01'
NC_CHAR = b'\x00\x00\x00\x02'
NC_SHORT = b'\x00\x00\x00\x03'
NC_INT = b'\x00\x00\x00\x04'
NC_FLOAT = b'\x00\x00\x00\x05'
NC_DOUBLE = b'\x00\x00\x00\x06'
NC_DIMENSION = b'\x00\x00\x00\n'
NC_VARIABLE = b'\x00\x00\x00\x0b'
NC_ATTRIBUTE = b'\x00\x00\x00\x0c'


TYPEMAP = {NC_BYTE: ('b', 1),
            NC_CHAR: ('c', 1),
            NC_SHORT: ('h', 2),
            NC_INT: ('i', 4),
            NC_FLOAT: ('f', 4),
            NC_DOUBLE: ('d', 8)}

REVERSE = {('b', 1): NC_BYTE,
            ('B', 1): NC_CHAR,
            ('c', 1): NC_CHAR,
            ('h', 2): NC_SHORT,
            ('i', 4): NC_INT,
            ('f', 4): NC_FLOAT,
            ('d', 8): NC_DOUBLE,

            # these come from asarray(1).dtype.char and asarray('foo').dtype.char,
            # used when getting the types from generic attributes.
            ('l', 4): NC_INT,
            ('S', 1): NC_CHAR}


class netcdf_file(object):
    """
    A file object for NetCDF data.

    A `netcdf_file` object has two standard attributes: `dimensions` and
    `variables`. The values of both are dictionaries, mapping dimension
    names to their associated lengths and variable names to variables,
    respectively. Application programs should never modify these
    dictionaries.

    All other attributes correspond to global attributes defined in the
    NetCDF file. Global file attributes are created by assigning to an
    attribute of the `netcdf_file` object.

    Parameters
    ----------
    filename : string or file-like
        string -> filename
    mode : {'r', 'w', 'a'}, optional
        read-write-append mode, default is 'r'
    mmap : None or bool, optional
        Whether to mmap `filename` when reading.  Default is True
        when `filename` is a file name, False when `filename` is a
        file-like object. Note that when mmap is in use, data arrays
        returned refer directly to the mmapped data on disk, and the
        file cannot be closed as long as references to it exist.
    version : {1, 2}, optional
        version of netcdf to read / write, where 1 means *Classic
        format* and 2 means *64-bit offset format*.  Default is 1.  See
        `here <http://www.unidata.ucar.edu/software/netcdf/docs/netcdf/Which-Format.html>`__
        for more info.
    maskandscale : bool, optional
        Whether to automatically scale and/or mask data based on attributes.
        Default is False.

    Notes
    -----
    The major advantage of this module over other modules is that it doesn't
    require the code to be linked to the NetCDF libraries. This module is
    derived from `pupynere <https://bitbucket.org/robertodealmeida/pupynere/>`_.

    NetCDF files are a self-describing binary data format. The file contains
    metadata that describes the dimensions and variables in the file. More
    details about NetCDF files can be found `here
    <http://www.unidata.ucar.edu/software/netcdf/docs/netcdf.html>`__. There
    are three main sections to a NetCDF data structure:

    1. Dimensions
    2. Variables
    3. Attributes

    The dimensions section records the name and length of each dimension used
    by the variables. The variables would then indicate which dimensions it
    uses and any attributes such as data units, along with containing the data
    values for the variable. It is good practice to include a
    variable that is the same name as a dimension to provide the values for
    that axes. Lastly, the attributes section would contain additional
    information such as the name of the file creator or the instrument used to
    collect the data.

    When writing data to a NetCDF file, there is often the need to indicate the
    'record dimension'. A record dimension is the unbounded dimension for a
    variable. For example, a temperature variable may have dimensions of
    latitude, longitude and time. If one wants to add more temperature data to
    the NetCDF file as time progresses, then the temperature variable should
    have the time dimension flagged as the record dimension.

    In addition, the NetCDF file header contains the position of the data in
    the file, so access can be done in an efficient manner without loading
    unnecessary data into memory. It uses the ``mmap`` module to create
    Numpy arrays mapped to the data on disk, for the same purpose.

    Note that when `netcdf_file` is used to open a file with mmap=True
    (default for read-only), arrays returned by it refer to data
    directly on the disk. The file should not be closed, and cannot be cleanly
    closed when asked, if such arrays are alive. You may want to copy data arrays
    obtained from mmapped Netcdf file if they are to be processed after the file
    is closed, see the example below.

    Examples
    --------
    To create a NetCDF file:

    >>> from scipy.io import netcdf
    >>> f = netcdf.netcdf_file('simple.nc', 'w')
    >>> f.history = 'Created for a test'
    >>> f.createDimension('time', 10)
    >>> time = f.createVariable('time', 'i', ('time',))
    >>> time[:] = np.arange(10)
    >>> time.units = 'days since 2008-01-01'
    >>> f.close()

    Note the assignment of ``range(10)`` to ``time[:]``.  Exposing the slice
    of the time variable allows for the data to be set in the object, rather
    than letting ``range(10)`` overwrite the ``time`` variable.

    To read the NetCDF file we just created:

    >>> from scipy.io import netcdf
    >>> f = netcdf.netcdf_file('simple.nc', 'r')
    >>> print(f.history)
    Created for a test
    >>> time = f.variables['time']
    >>> print(time.units)
    days since 2008-01-01
    >>> print(time.shape)
    (10,)
    >>> print(time[-1])
    9

    NetCDF files, when opened read-only, return arrays that refer
    directly to memory-mapped data on disk:

    >>> data = time[:]
    >>> data.base.base
    <mmap.mmap object at 0x7fe753763180>

    If the data is to be processed after the file is closed, it needs
    to be copied to main memory:

    >>> data = time[:].copy()
    >>> f.close()
    >>> data.mean()
    4.5

    A NetCDF file can also be used as context manager:

    >>> from scipy.io import netcdf
    >>> with netcdf.netcdf_file('simple.nc', 'r') as f:
    ...     print(f.history)
    Created for a test

    """
    def __init__(self, filename, mode='r', mmap=None, version=1,
                 maskandscale=False):
        """Initialize netcdf_file from fileobj (str or file-like)."""
        if mode not in 'rwa':
            raise ValueError("Mode must be either 'r', 'w' or 'a'.")

        if hasattr(filename, 'seek'):  # file-like
            self.fp = fs_utils.tmpfs_copy(filename)
            self.filename = 'None'
            if mmap is None:
                mmap = False
            elif mmap and not hasattr(filename, 'fileno'):
                raise ValueError('Cannot use file object for mmap')
        else:  # maybe it's a string
            self.filename = fs_utils.tmpfs_copy(filename)
            omode = 'r+' if mode == 'a' else mode
            self.fp = open(self.filename, '%sb' % omode)
            if mmap is None:
                mmap = True

        if mode != 'r':
            # Cannot read write-only files
            mmap = False

        self.use_mmap = mmap
        self.mode = mode
        self.version_byte = version
        self.maskandscale = maskandscale

        self.dimensions = {}
        self.variables = {}

        self._dims = []
        self._recs = 0
        self._recsize = 0

        self._mm = None
        self._mm_buf = None
        if self.use_mmap:
            self._mm = mm.mmap(self.fp.fileno(), 0, access=mm.ACCESS_READ)
            self._mm_buf = np.frombuffer(self._mm, dtype=np.int8)

        self._attributes = {}

        if mode in 'ra':
            self._read()

    def __setattr__(self, attr, value):
        # Store user defined attributes in a separate dict,
        # so we can save them to file later.
        try:
            self._attributes[attr] = value
        except AttributeError:
            pass
        self.__dict__[attr] = value

    def close(self):
        """Closes the NetCDF file."""
        if not self.fp.closed:
            self.variables = {}
            if self._mm_buf is not None:
                ref = weakref.ref(self._mm_buf)
                self._mm_buf = None
                if ref() is None:
                    # self._mm_buf is gc'd, and we can close the mmap
                    self._mm.close()
                else:
                    # we cannot close self._mm, since self._mm_buf is
                    # alive and there may still be arrays referring to it
                    warnings.warn((
                            "Cannot close a netcdf_file opened with mmap=True, when "
                            "netcdf_variables or arrays referring to its data still exist. "
                            "All data arrays obtained from such files refer directly to "
                            "data on disk, and must be copied before the file can be cleanly "
                            "closed. (See netcdf_file docstring for more information on mmap.)"
                            ), category=RuntimeWarning)
            self._mm = None
            self.fp.close()
        os.remove(self.filename)
    __del__ = close

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _read(self):
        # Check magic bytes and version
        magic = self.fp.read(3)
        if not magic == b'CDF':
            raise TypeError("Error: %s is not a valid NetCDF 3 file" %
                            self.filename)
        self.__dict__['version_byte'] = fromstring(self.fp.read(1), '>b')[0]

        # Read file headers and set data.
        self._read_numrecs()
        self._read_dim_array()
        self._read_gatt_array()
        self._read_var_array()

    def _read_numrecs(self):
        self.__dict__['_recs'] = self._unpack_int()

    def _read_dim_array(self):
        header = self.fp.read(4)
        if header not in [ZERO, NC_DIMENSION]:
            raise ValueError("Unexpected header.")
        count = self._unpack_int()

        for dim in range(count):
            name = asstr(self._unpack_string())
            length = self._unpack_int() or None  # None for record dimension
            self.dimensions[name] = length
            self._dims.append(name)  # preserve order

    def _read_gatt_array(self):
        for k, v in self._read_att_array().items():
            self.__setattr__(k, v)

    def _read_att_array(self):
        header = self.fp.read(4)
        if header not in [ZERO, NC_ATTRIBUTE]:
            raise ValueError("Unexpected header.")
        count = self._unpack_int()

        attributes = {}
        for attr in range(count):
            name = asstr(self._unpack_string())
            attributes[name] = self._read_values()
        return attributes

    def _read_var_array(self):
        header = self.fp.read(4)
        if header not in [ZERO, NC_VARIABLE]:
            raise ValueError("Unexpected header.")

        begin = 0
        dtypes = {'names': [], 'formats': []}
        rec_vars = []
        count = self._unpack_int()
        for var in range(count):
            (name, dimensions, shape, attributes,
             typecode, size, dtype_, begin_, vsize) = self._read_var()
            # http://www.unidata.ucar.edu/software/netcdf/docs/netcdf.html
            # Note that vsize is the product of the dimension lengths
            # (omitting the record dimension) and the number of bytes
            # per value (determined from the type), increased to the
            # next multiple of 4, for each variable. If a record
            # variable, this is the amount of space per record. The
            # netCDF "record size" is calculated as the sum of the
            # vsize's of all the record variables.
            #
            # The vsize field is actually redundant, because its value
            # may be computed from other information in the header. The
            # 32-bit vsize field is not large enough to contain the size
            # of variables that require more than 2^32 - 4 bytes, so
            # 2^32 - 1 is used in the vsize field for such variables.
            if shape and shape[0] is None:  # record variable
                rec_vars.append(name)
                # The netCDF "record size" is calculated as the sum of
                # the vsize's of all the record variables.
                self.__dict__['_recsize'] += vsize
                if begin == 0:
                    begin = begin_
                dtypes['names'].append(name)
                dtypes['formats'].append(str(shape[1:]) + dtype_)

                # Handle padding with a virtual variable.
                if typecode in 'bch':
                    actual_size = reduce(mul, (1,) + shape[1:]) * size
                    padding = -actual_size % 4
                    if padding:
                        dtypes['names'].append('_padding_%d' % var)
                        dtypes['formats'].append('(%d,)>b' % padding)

                # Data will be set later.
                data = None
            else:  # not a record variable
                # Calculate size to avoid problems with vsize (above)
                a_size = reduce(mul, shape, 1) * size
                if self.use_mmap:
                    data = self._mm_buf[begin_:begin_+a_size].view(dtype=dtype_)
                    data.shape = shape
                else:
                    pos = self.fp.tell()
                    self.fp.seek(begin_)
                    data = fromstring(self.fp.read(a_size), dtype=dtype_)
                    data.shape = shape
                    self.fp.seek(pos)

            # Add variable.
            self.variables[name] = netcdf_variable(
                    data, typecode, size, shape, dimensions, attributes,
                    maskandscale=self.maskandscale)

        if rec_vars:
            # Remove padding when only one record variable.
            if len(rec_vars) == 1:
                dtypes['names'] = dtypes['names'][:1]
                dtypes['formats'] = dtypes['formats'][:1]

            # Build rec array.
            if self.use_mmap:
                rec_array = self._mm_buf[begin:begin+self._recs*self._recsize].view(dtype=dtypes)
                rec_array.shape = (self._recs,)
            else:
                pos = self.fp.tell()
                self.fp.seek(begin)
                rec_array = fromstring(self.fp.read(self._recs*self._recsize), dtype=dtypes)
                rec_array.shape = (self._recs,)
                self.fp.seek(pos)

            for var in rec_vars:
                self.variables[var].__dict__['data'] = rec_array[var]

    def _read_var(self):
        name = asstr(self._unpack_string())
        dimensions = []
        shape = []
        dims = self._unpack_int()

        for i in range(dims):
            dimid = self._unpack_int()
            dimname = self._dims[dimid]
            dimensions.append(dimname)
            dim = self.dimensions[dimname]
            shape.append(dim)
        dimensions = tuple(dimensions)
        shape = tuple(shape)

        attributes = self._read_att_array()
        nc_type = self.fp.read(4)
        vsize = self._unpack_int()
        begin = [self._unpack_int, self._unpack_int64][self.version_byte-1]()

        typecode, size = TYPEMAP[nc_type]
        dtype_ = '>%s' % typecode

        return name, dimensions, shape, attributes, typecode, size, dtype_, begin, vsize

    def _read_values(self):
        nc_type = self.fp.read(4)
        n = self._unpack_int()

        typecode, size = TYPEMAP[nc_type]

        count = n*size
        values = self.fp.read(int(count))
        self.fp.read(-count % 4)  # read padding

        if typecode is not 'c':
            values = fromstring(values, dtype='>%s' % typecode)
            if values.shape == (1,):
                values = values[0]
        else:
            values = values.rstrip(b'\x00')
        return values

    def _pack_begin(self, begin):
        if self.version_byte == 1:
            self._pack_int(begin)
        elif self.version_byte == 2:
            self._pack_int64(begin)

    def _pack_int(self, value):
        self.fp.write(array(value, '>i').tostring())
    _pack_int32 = _pack_int

    def _unpack_int(self):
        return int(fromstring(self.fp.read(4), '>i')[0])
    _unpack_int32 = _unpack_int

    def _pack_int64(self, value):
        self.fp.write(array(value, '>q').tostring())

    def _unpack_int64(self):
        return fromstring(self.fp.read(8), '>q')[0]

    def _pack_string(self, s):
        count = len(s)
        self._pack_int(count)
        self.fp.write(asbytes(s))
        self.fp.write(b'0' * (-count % 4))  # pad

    def _unpack_string(self):
        count = self._unpack_int()
        s = self.fp.read(count).rstrip(b'\x00')
        self.fp.read(-count % 4)  # read padding
        return s


class netcdf_variable(object):
    """
    A data object for the `netcdf` module.

    `netcdf_variable` objects are constructed by calling the method
    `netcdf_file.createVariable` on the `netcdf_file` object. `netcdf_variable`
    objects behave much like array objects defined in numpy, except that their
    data resides in a file. Data is read by indexing and written by assigning
    to an indexed subset; the entire array can be accessed by the index ``[:]``
    or (for scalars) by using the methods `getValue` and `assignValue`.
    `netcdf_variable` objects also have attribute `shape` with the same meaning
    as for arrays, but the shape cannot be modified. There is another read-only
    attribute `dimensions`, whose value is the tuple of dimension names.

    All other attributes correspond to variable attributes defined in
    the NetCDF file. Variable attributes are created by assigning to an
    attribute of the `netcdf_variable` object.

    Parameters
    ----------
    data : array_like
        The data array that holds the values for the variable.
        Typically, this is initialized as empty, but with the proper shape.
    typecode : dtype character code
        Desired data-type for the data array.
    size : int
        Desired element size for the data array.
    shape : sequence of ints
        The shape of the array.  This should match the lengths of the
        variable's dimensions.
    dimensions : sequence of strings
        The names of the dimensions used by the variable.  Must be in the
        same order of the dimension lengths given by `shape`.
    attributes : dict, optional
        Attribute values (any type) keyed by string names.  These attributes
        become attributes for the netcdf_variable object.
    maskandscale : bool, optional
        Whether to automatically scale and/or mask data based on attributes.
        Default is False.


    Attributes
    ----------
    dimensions : list of str
        List of names of dimensions used by the variable object.
    isrec, shape
        Properties

    See also
    --------
    isrec, shape

    """
    def __init__(self, data, typecode, size, shape, dimensions,
                 attributes=None,
                 maskandscale=False):
        self.data = data
        self._typecode = typecode
        self._size = size
        self._shape = shape
        self.dimensions = dimensions
        self.maskandscale = maskandscale

        self._attributes = attributes or {}
        for k, v in self._attributes.items():
            self.__dict__[k] = v

    def __setattr__(self, attr, value):
        # Store user defined attributes in a separate dict,
        # so we can save them to file later.
        try:
            self._attributes[attr] = value
        except AttributeError:
            pass
        self.__dict__[attr] = value

    def isrec(self):
        """Returns whether the variable has a record dimension or not.

        A record dimension is a dimension along which additional data could be
        easily appended in the netcdf data structure without much rewriting of
        the data file. This attribute is a read-only property of the
        `netcdf_variable`.

        """
        return bool(self.data.shape) and not self._shape[0]
    isrec = property(isrec)

    def shape(self):
        """Returns the shape tuple of the data variable.

        This is a read-only attribute and can not be modified in the
        same manner of other numpy arrays.
        """
        return self.data.shape
    shape = property(shape)

    def getValue(self):
        """
        Retrieve a scalar value from a `netcdf_variable` of length one.

        Raises
        ------
        ValueError
            If the netcdf variable is an array of length greater than one,
            this exception will be raised.

        """
        return self.data.item()

    def assignValue(self, value):
        """
        Assign a scalar value to a `netcdf_variable` of length one.

        Parameters
        ----------
        value : scalar
            Scalar value (of compatible type) to assign to a length-one netcdf
            variable. This value will be written to file.

        Raises
        ------
        ValueError
            If the input is not a scalar, or if the destination is not a length-one
            netcdf variable.

        """
        if not self.data.flags.writeable:
            # Work-around for a bug in NumPy.  Calling itemset() on a read-only
            # memory-mapped array causes a seg. fault.
            # See NumPy ticket #1622, and SciPy ticket #1202.
            # This check for `writeable` can be removed when the oldest version
            # of numpy still supported by scipy contains the fix for #1622.
            raise RuntimeError("variable is not writeable")

        self.data.itemset(value)

    def typecode(self):
        """
        Return the typecode of the variable.

        Returns
        -------
        typecode : char
            The character typecode of the variable (eg, 'i' for int).

        """
        return self._typecode

    def itemsize(self):
        """
        Return the itemsize of the variable.

        Returns
        -------
        itemsize : int
            The element size of the variable (eg, 8 for float64).

        """
        return self._size

    def __getitem__(self, index):
        if not self.maskandscale:
            return self.data[index]

        data = self.data[index].copy()
        missing_value = self._get_missing_value()
        data = self._apply_missing_value(data, missing_value)
        scale_factor = self._attributes.get('scale_factor')
        add_offset = self._attributes.get('add_offset')
        if add_offset is not None or scale_factor is not None:
            data = data.astype(np.float64)
        if scale_factor is not None:
            data = data * scale_factor
        if add_offset is not None:
            data += add_offset

        return data

    def __setitem__(self, index, data):
        if self.maskandscale:
            missing_value = (
                    self._get_missing_value() or
                    getattr(data, 'fill_value', 999999))
            self._attributes.setdefault('missing_value', missing_value)
            self._attributes.setdefault('_FillValue', missing_value)
            data = ((data - self._attributes.get('add_offset', 0.0)) /
                    self._attributes.get('scale_factor', 1.0))
            data = np.ma.asarray(data).filled(missing_value)
            if self._typecode not in 'fd' and data.dtype.kind == 'f':
                data = np.round(data)

        # Expand data for record vars?
        if self.isrec:
            if isinstance(index, tuple):
                rec_index = index[0]
            else:
                rec_index = index
            if isinstance(rec_index, slice):
                recs = (rec_index.start or 0) + len(data)
            else:
                recs = rec_index + 1
            if recs > len(self.data):
                shape = (recs,) + self._shape[1:]
                self.data.resize(shape)
        self.data[index] = data

    def _get_missing_value(self):
        """
        Returns the value denoting "no data" for this variable.

        If this variable does not have a missing/fill value, returns None.

        If both _FillValue and missing_value are given, give precedence to
        _FillValue. The netCDF standard gives special meaning to _FillValue;
        missing_value is  just used for compatibility with old datasets.
        """

        if '_FillValue' in self._attributes:
            missing_value = self._attributes['_FillValue']
        elif 'missing_value' in self._attributes:
            missing_value = self._attributes['missing_value']
        else:
            missing_value = None

        return missing_value

    @staticmethod
    def _apply_missing_value(data, missing_value):
        """
        Applies the given missing value to the data array.

        Returns a numpy.ma array, with any value equal to missing_value masked
        out (unless missing_value is None, in which case the original array is
        returned).
        """

        if missing_value is None:
            newdata = data
        else:
            try:
                missing_value_isnan = np.isnan(missing_value)
            except (TypeError, NotImplementedError):
                # some data types (e.g., characters) cannot be tested for NaN
                missing_value_isnan = False

            if missing_value_isnan:
                mymask = np.isnan(data)
            else:
                mymask = (data == missing_value)

            newdata = np.ma.masked_where(mymask, data)

        return newdata


NetCDFFile = netcdf_file
NetCDFVariable = netcdf_variable
