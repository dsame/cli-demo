import os
import sys
import tempfile

from oml.model import Model
from oml.factory import TemplateFactory
from oml.settings import PYTHON_LANG
from unittest import mock, skipUnless, TestCase


class TestQASPythonModel(TestCase):

    def setUp(self):
        self.tmp_dirpath = tempfile.mkdtemp()
        factory = TemplateFactory(PYTHON_LANG)
        factory.generate(self.tmp_dirpath, 'pytorch', 'Release', 'qas')
        os.chdir(self.tmp_dirpath)
        self.model = Model(self.tmp_dirpath)

    def test_eval(self):
        self.model.eval()
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, '.score')), True)

    @mock.patch('oml.models.python.PythonModel.serve')
    def test_serve(self, mock_serve):
        self.model.serve()
        self.assertEqual(mock_serve.call_count, 1)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    @mock.patch('shutil.rmtree')
    @mock.patch('subprocess.run')
    def test_QAS_package_without_platform(self, mock_subprocess, mock_rmtree):
        package_path = os.path.join(self.tmp_dirpath, '.oml', 'package')
        conda_package_path = os.path.join(self.tmp_dirpath, '.oml', 'env', self.model.model_name)
        os.makedirs(conda_package_path, exist_ok=True)
        self.assertEqual(os.path.exists(conda_package_path), True)
        # hide platform in package command, read from oml.yml
        self.assertEqual(self.model.metadata['platform'], 'qas')
        self.model.package(None, skip_archive=False)
        self.assertEqual(mock_rmtree.call_count, 1)
        self.assertEqual(os.path.exists(package_path), True)
        self.assertEqual(os.path.exists(os.path.join(package_path, 'conda',
            '{}.zip'.format(self.model.model_name))), True)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    @mock.patch('shutil.rmtree')
    @mock.patch('subprocess.run')
    def test_QAS_package_without_platform_with_skip_archive(self, mock_subprocess, mock_rmtree):
        package_path = os.path.join(self.tmp_dirpath, '.oml', 'package')
        conda_package_path = os.path.join(self.tmp_dirpath, '.oml', 'env', self.model.model_name)
        os.makedirs(conda_package_path, exist_ok=True)
        self.assertEqual(os.path.exists(conda_package_path), True)
        # hide platform in package command, read from oml.yml
        self.assertEqual(self.model.metadata['platform'], 'qas')
        self.model.package(None, skip_archive=True)
        self.assertEqual(mock_rmtree.call_count, 1)
        self.assertEqual(os.path.exists(package_path), True)
        self.assertEqual(os.path.exists(os.path.join(package_path, 'conda',
            '{}.zip'.format(self.model.model_name))), False)
