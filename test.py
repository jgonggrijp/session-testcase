# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Runs all the tests in the suite.
"""

import unittest

from reduced_testcase.tests import suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite)
