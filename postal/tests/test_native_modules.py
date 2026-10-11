import unittest

from postal.dedupe import duplicate_status, is_street_duplicate
from postal.near_dupe import name_hashes, near_dupe_hashes
from postal.normalize import normalize_string, normalized_tokens
from postal.tokenize import tokenize


class TestNativeModules(unittest.TestCase):
    def test_native_modules(self):
        self.assertEqual([word for word, _ in tokenize('781 Franklin Ave')],
                         ['781', 'Franklin', 'Ave'])
        self.assertEqual(normalize_string('Cércle rouge'), 'cercle rouge')
        self.assertTrue(normalized_tokens('St.-Barthélemy'))
        self.assertTrue(name_hashes('The Book Club', languages=['en']))
        self.assertTrue(near_dupe_hashes(['house', 'house_number', 'road', 'city'],
                                       ['The Book Club', '781', 'Franklin Avenue', 'Brooklyn'],
                                       languages=['en']))
        self.assertEqual(is_street_duplicate('Franklin Ave', 'Franklin Avenue',
                                            languages=['en']),
                         duplicate_status.EXACT_DUPLICATE)
