import os
import shutil
import tempfile
import unittest

from oml.util.os import touch
from oml.util.zip import archive, extract


class ZipTest(unittest.TestCase):

    def setUp(self):
        self.tmp_path = tempfile.mkdtemp()
        self.zip_dir = 'test'
        self.zip_path = os.path.join(self.tmp_path, self.zip_dir)
        os.makedirs(self.zip_path, exist_ok=True)

        # Create dummy files
        for x in range(5):
            touch(os.path.join(self.zip_path, '{}.txt'.format(x)))

    def tearDown(self):
        if os.path.exists(self.tmp_path):
            os.chdir(os.path.expanduser('~'))
            shutil.rmtree(self.tmp_path)

    def test_archive(self):
        zipf = archive(self.zip_path, self.tmp_path, self.zip_dir)
        answer = os.path.realpath(os.path.join(self.tmp_path, '{}.zip'.format(self.zip_dir)))
        self.assertEqual(zipf, answer)
        self.assertTrue(os.path.exists(zipf))

    def test_extract(self):
        zipf = archive(self.zip_path, self.tmp_path, self.zip_dir)
        dirpath = os.path.join(self.tmp_path, 'new')
        extract(zipf, dirpath)
        self.assertTrue(os.path.exists(dirpath))
