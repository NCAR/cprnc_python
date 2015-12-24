class netcdf_fake:
    """Fake replacement for a netcdf adapter, for the sake of unit testing.

    This version allows unit tests to add whatever data they want before calling
    a method on the system under test."""
    # ------------------------------------------------------------------------
    # Test-specific interface
    # ------------------------------------------------------------------------
    def __init__(self, filename, variables={}, global_attributes={}):
        """Initialize a netcdf_fake instance.

        Arguments:

        filename: string giving the fake filename (this is not actually read, so
        can be a nonexistent file)

        variables: dictionary of variables, where the values are typically numpy or
        numpy.ma arrays (variables can be added later with add_variable)

        global_attributes: dictionary of "global attributes" of the fake file
        """
        self._variables = variables
        self._filename = filename
        self._global_attributes = global_attributes

    def add_variable(self, varname, data):
        """Add a variable to the variable dictionary.

        Arguments:
        varname: string
        data: numpy or numpy.ma array
        """
        self._variables[varname] = data

    # ------------------------------------------------------------------------
    # Replacements for real functionality
    # ------------------------------------------------------------------------
    def get_varlist(self):
        """Returns an iterable list of variables in the netcdf file"""
        return self._variables.keys()

    def get_vardata(self, varname):
        return self._variables[varname]

    def get_filename(self):
        return self._filename

    def get_global_attributes(self):
        return self._global_attributes
    
