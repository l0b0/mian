#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mian test suite

Default syntax:

./tests.py
    Run all unit tests
"""

__author__ = 'Victor Engmark'
__copyright__ = 'Copyright (C) 2010 Victor Engmark'
__maintainer__ = 'Victor Engmark'
__email__ = 'victor.engmark@gmail.com'
__license__ = 'GPL v3 or newer'

from doctest import testmod
import unittest

from mian import mian


class TestLookup(unittest.TestCase):
    """Framework for testing lookup of block types."""
    # pylint: disable-msg=R0904

    def test_substring(self):
        """Substring match."""
        self.assertEquals(
            mian._lookup_block_type('gold'),
            {'\x29': 'Gold block', '\x0e': 'Gold ore'})


    def test_hex(self):
        """Hex ID match."""
        self.assertEquals(
            mian._lookup_block_type('20'),
            {'\x20': 'Magenta cloth'})


class TestDoc(unittest.TestCase):
    """Test Python documentation strings."""
    def test_doc(self):
        """Documentation tests."""
        self.assertEqual(testmod(mian)[0], 0)


def main():
    """Run tests"""
    unittest.main()


if __name__ == '__main__':
    main()
