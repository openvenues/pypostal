# -*- coding: utf-8 -*-
"""Test pypostal address parsing."""

from __future__ import unicode_literals

import unittest
from postal.parser import parse_address


class TestParser(unittest.TestCase):
    """Test libpostal address parser from Python."""

    def contains_components(self, address, components):
        """Test whether address parse contains specific components."""
        expected = len(components)
        got = 0

        parsed = parse_address(address)
        self.assertTrue(parsed)

        for s, c in parsed:
            if components.get(c, None) == s:
                got += 1

        self.assertEqual(expected, got)

    def test_parses(self):
        """Parser tests."""
        self.contains_components('781 Franklin Ave Crown Heights Brooklyn NYC NY 11216 USA',{
                                 'house_number': '781',
                                 'road': 'franklin ave',
                                 'suburb': 'crown heights',
                                 'city_district': 'brooklyn',
                                 'city': 'nyc',
                                 'state': 'ny',
                                 'postcode': '11216',
                                 'country': 'usa'
                                 })


if __name__ == '__main__':
    unittest.main()
