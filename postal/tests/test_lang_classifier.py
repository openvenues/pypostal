# -*- coding: utf-8 -*-
"""Test pypostal address parsing."""

from __future__ import unicode_literals

import unittest
from postal.lang_classifier import classify_lang_address


class TestLangClassfier(unittest.TestCase):
    """Test libpostal language classifier from Python."""
    def test_parses(self):
        cases = (
            ('Rua casemiro osorio, 123', {'pt': 1.0}),
            ('Street Oudenoord, 1234', {'en': 0.76, 'nl': 0.23}),
            ('Oudenoord, 1234', {'nl': 1.0})
        )

        """Language classifier tests."""
        for address, lang_expected in cases:
            lang = classify_lang_address(address)
            # Round probabilities
            lang = {k: round(v, 2) for k, v in lang}
            self.assertDictEqual(lang, lang_expected)


if __name__ == '__main__':
    unittest.main()
