import unittest

from oml import settings


class SettingsTest(unittest.TestCase):

    def test_loading_conf_file(self):
        self.assertIsNotNone(settings.cfg)
