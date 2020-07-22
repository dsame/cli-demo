import unittest

from oml.util.version import is_int, increment, latest


class VersionTest(unittest.TestCase):

    def test_is_int(self):
        self.assertEqual(is_int('1'), True)
        self.assertEqual(is_int('a'), False)

    def test_increment(self):
        self.assertEqual(increment('0.0.1'), '0.0.2')
        self.assertEqual(increment('0.0.1', 'major'), '1.0.0')
        self.assertEqual(increment('0.0.1', 'minor'), '0.1.0')
        self.assertEqual(increment('0.0.1', 'patch'), '0.0.2')

        try:
            increment('1.0.a')
        except ValueError as e:
            self.assertIsInstance(e, ValueError)

    def test_latest(self):
        self.assertEqual(latest(['11.2.1', '2.5.1', '1.12.1']), '11.2.1')
        self.assertEqual(latest(['1.0.0']), '1.0.0')
        self.assertEqual(latest([]), None)
