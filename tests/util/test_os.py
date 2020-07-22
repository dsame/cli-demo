import os
import platform
import shutil
import tempfile
import unittest

from stat import ST_MODE
from oml.util.os import touch, rchmod


class OsTest(unittest.TestCase):

    def setUp(self):
        self.tmp_path = tempfile.mkdtemp()
        self.fpath = os.path.join(self.tmp_path, 'run.sh')

    def tearDown(self):
        if os.path.exists(self.tmp_path):
            shutil.rmtree(self.tmp_path)

    def test_touch(self):
        touch(self.fpath)
        self.assertTrue(os.path.exists(self.fpath))

    def test_rchmod(self):
        if platform.system() != 'Windows':
            touch(self.fpath)
            rchmod(self.fpath, 0o744)
            self.assertTrue(oct(os.stat(self.fpath)[ST_MODE])[-3:], 0o744)
