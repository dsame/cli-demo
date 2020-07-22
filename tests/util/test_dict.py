import unittest

from oml.util.dict import keys_exists


class DictTest(unittest.TestCase):

    def test_dict(self):
        di = {'test': {'test': 'test'}}
        self.assertEqual(keys_exists(di, 'test', 'test'), True)
