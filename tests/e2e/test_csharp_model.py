import os
import sys
import tempfile

from oml.model import Model
from oml.factory import TemplateFactory
from oml.settings import CSHARP_LANG
from unittest import mock, skipUnless, TestCase


class TestCSharpModel(TestCase):

    def setUp(self):
        self.tmp_dirpath = tempfile.mkdtemp()
        factory = TemplateFactory(CSHARP_LANG)
        factory.generate(self.tmp_dirpath, 'tensorflow', 'Release')
        self.model = Model(self.tmp_dirpath)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    def test_unit_tests(self):
        os.chdir(self.tmp_dirpath)
        self.model.test()
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, 'UnitTest', 'TestResults')), True)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    @mock.patch('oml.models.csharp.CSharpModel.serve')
    def test_serve(self, mock_serve):
        self.model.serve()
        self.assertEqual(mock_serve.call_count, 1)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    def test_eval(self):
        self.model.eval()
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, '.score')), True)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    def test_package(self):
        self.model.package('dlisv3', skip_archive=False)
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, '.oml', 'package')), True)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    def test_manifest(self):
        self.model.package('dlisv3', skip_archive=False)
        self.model.create_manifests()
        manifest_path = os.path.join(self.tmp_dirpath, '.oml', 'package', 'SecureManifest.json')
        self.assertEqual(os.path.exists(manifest_path), True)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    def test_package_dlisv3binary(self):
        self.model.package('dlisv3binary', skip_archive=False)
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, '.oml', 'package')), True)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    def test_manifest_dlisv3binary(self):
        self.model.package('dlisv3binary', skip_archive=False)
        self.model.create_manifests()
        manifest_path = os.path.join(self.tmp_dirpath, '.oml', 'package', 'SecureManifest.json')
        self.assertEqual(os.path.exists(manifest_path), True)
