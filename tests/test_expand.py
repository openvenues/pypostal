# -*- coding: utf-8 -*-
"""Test pypostal expansions."""

from __future__ import unicode_literals

import unittest
from postal.expand import *


class TestExpand(unittest.TestCase):
    """Test expansions."""

    def contained_in_root_expansions(self, address, output, **kw):
        expansions = expand_address_root(address, **kw)
        self.assertTrue(expansions)

        expansions = set(expansions)
        self.assertTrue(output in expansions)

    def contained_in_expansions(self, address, output, **kw):
        """Test whether an expansion contains a particular output."""
        expansions = expand_address(address, **kw)
        self.assertTrue(expansions)

        expansions = set(expansions)
        self.assertTrue(output in expansions)

    def have_expansion_in_common(self, str1, str2, **kw):
        """Test whether strings have at least one shared expansion."""
        expansions1 = expand_address(str1, **kw)
        expansions2 = expand_address(str2, **kw)

        self.assertTrue(set(expansions1) & set(expansions2))

    def has_exact_expansions(self, address, expected_expansions, **kw):
        """Test whether an address expands exactly"""
        expansions = expand_address(address, **kw)
        self.assertTrue(expansions)

        expansions = set(expansions)
        expected_expansions = set(expected_expansions)
        self.assertTrue(expansions == expected_expansions)

    def test_expansions(self):
        """Expansion tests."""
        self.contained_in_expansions('781 Franklin Ave Crown Hts Brooklyn NY', '781 franklin avenue crown heights brooklyn new york')

        self.have_expansion_in_common('Thirty W 26th St Fl #7', '30 West Twenty-sixth Street Floor Number 7', languages=['en'])

        self.contained_in_expansions('Friedrichstraße 128, Berlin, Germany', 'friedrich strasse 128 berlin germany')

        self.contained_in_expansions('MAPLE ST.', 'maple street')
        self.contained_in_expansions('ST ISIDORE DR', 'saint isidore drive')
        self.contained_in_expansions('ST. Sebastian ST', 'saint sebastian street')
        self.contained_in_expansions("St John's St.", 'saint johns street')
        self.contained_in_expansions('MORNINGTON CR', 'mornington crescent')
        self.contained_in_expansions('Cércle rouge', 'cercle rouge')
        self.contained_in_expansions('Third St', '3rd street')

        self.contained_in_expansions('123 Dr. MLK Jr. Dr.', '123 doctor martin luther king junior drive')

        self.has_exact_expansions('120 Malcolm X Blvd', ['120 malcolm x boulevard'], roman_numerals=False)

    def test_root_expansions(self):
        self.contained_in_root_expansions("E 106TH ST", "106", address_components=ADDRESS_STREET | ADDRESS_ANY, languages=['en'])
        self.contained_in_root_expansions("PARK AVE", "park", address_components=ADDRESS_STREET | ADDRESS_ANY, languages=['en'])

if __name__ == '__main__':
    unittest.main()
