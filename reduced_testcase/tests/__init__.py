# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Top-level test suite to rule them all.
"""

import unittest

import test_server, test_admin

suite = unittest.TestSuite([
    test_server.suite,
    unittest.TestLoader().loadTestsFromModule(test_admin),
])

if __name__ == '__main__':
    unittest.main()
