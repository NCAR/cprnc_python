import numpy as np
import numpy.ma as ma
import unittest

class CustomAssertions(unittest.TestCase):
    """
    This class provides custom assertions for unit testing.

    Our unit test classes can inherit from this rather than from
    unittest.TestCase
    """

    def assertArraysEqual(self, arr1, arr2):
        """
        Ensure that two numpy / numpy.ma arrays are equivalent in both their
        mask and their data.
        """
        if (arr1.shape != arr2.shape):
            msg = "Shapes differ:\n" + \
              str(arr1.shape) + " != " + str(arr2.shape)
            raise AssertionError(msg)

        mask1 = ma.getmaskarray(arr1)
        mask2 = ma.getmaskarray(arr2)
        masks_equal = np.array_equal(mask1, mask2)
        if (not masks_equal):
            msg = "Masks differ:\n" + \
              str(mask1) + " != " + str(mask2) + "\n" + \
              "Arrays are: \n" + \
              str(arr1) + "\n" + \
              str(arr2)

            raise AssertionError(msg)

        vals_equal = ma.allequal(arr1, arr2)
        if (not vals_equal):
            msg = "Values differ:\n" + \
              str(arr1) + " != " + str(arr2)
            raise AssertionError(msg)

    def assertRegexMatches(self, string, regex):
        """
        Wrapper for assertRegexpMatches (python2) / assertRegex (python3).

        We could use the six package for this purpose, but six doesn't support
        the complementary assertNotRegexpMatches, so I'm implementing this
        myself.
        """

        if (hasattr(self, 'assertRegex')):
            self.assertRegex(string, regex)
        elif (hasattr(self, 'assertRegexpMatches')):
            self.assertRegexpMatches(string, regex)
        else:
            raise NotImplementedError("This version of unittest does not"
                                      "implement assertRegex")

    def assertNotRegexMatches(self, string, regex):
        """
        Wrapper for assertNotRegexpMatches (python2) / assertNotRegex (python3).

        The six package does not support this, so I'm implementing it here.
        """

        if (hasattr(self, 'assertNotRegex')):
            self.assertNotRegex(string, regex)
        elif (hasattr(self, 'assertNotRegexpMatches')):
            self.assertNotRegexpMatches(string, regex)
        else:
            raise NotImplementedError("This version of unittest does not"
                                      "implement assertNotRegex")

    def assertSameItems(self, actual, expected):
        """
        Wrapper for assertItemsEqual (python2) / assertCountEqual (python3).

        We could use the six package for this purpose, but since I'm already
        handling other assertions here, I'm adding this one for consistency.
        """

        if (hasattr(self, 'assertCountEqual')):
            self.assertCountEqual(actual, expected)
        elif (hasattr(self, 'assertItemsEqual')):
            self.assertItemsEqual(actual, expected)
        else:
            raise NotImplementedError("This version of unittest does not"
                                      "implement assertCountEqual")
