"""Utilities for printing cprnc output"""

# ------------------------------------------------------------------------
# Public functions
# ------------------------------------------------------------------------

def index_str(indices):
    """Convert a list of indices into a pretty string for printing."""

    if (type(indices) == int or len(indices) == 0):
        return ""
    else:
        return "(" + ",".join([_format_index(index) for index in indices]) + ")"


# ------------------------------------------------------------------------
# Private functions
# ------------------------------------------------------------------------

def _format_index(index):
    """Return a string version of the given array index"""

    return "{:6d}".format(index)

