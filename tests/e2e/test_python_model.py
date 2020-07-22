import os
import sys
import tempfile

from click.testing import CliRunner
from oml.cli import main
from oml.model import Model
from oml.factory import TemplateFactory
from oml.settings import PYTHON_LANG
from unittest import mock, skipUnless, TestCase


class TestPythonModel(TestCase):

    def setUp(self):
        self.tmp_dirpath = tempfile.mkdtemp()
        factory = TemplateFactory(PYTHON_LANG)
        factory.generate(self.tmp_dirpath)
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
    def test_package(self, mock_subprocess, mock_rmtree):
        package_path = os.path.join(self.tmp_dirpath, '.oml', 'package')
        conda_package_path = os.path.join(self.tmp_dirpath, '.oml', 'env', self.model.model_name)
        os.makedirs(conda_package_path, exist_ok=True)
        self.assertEqual(os.path.exists(conda_package_path), True)
        self.model.package('dlis', skip_archive=False)
        self.assertEqual(mock_rmtree.call_count, 1)
        self.assertEqual(os.path.exists(package_path), True)
        self.assertEqual(os.path.exists(os.path.join(package_path, 'conda',
            '{}.zip'.format(self.model.model_name))), True)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    @mock.patch('shutil.rmtree')
    @mock.patch('subprocess.run')
    def test_package_with_skip_archive(self, mock_subprocess, mock_rmtree):
        package_path = os.path.join(self.tmp_dirpath, '.oml', 'package')
        conda_package_path = os.path.join(self.tmp_dirpath, '.oml', 'env', self.model.model_name)
        os.makedirs(conda_package_path, exist_ok=True)
        self.assertEqual(os.path.exists(conda_package_path), True)
        self.model.package('dlis', skip_archive=True)
        self.assertEqual(mock_rmtree.call_count, 1)
        self.assertEqual(os.path.exists(package_path), True)
        self.assertEqual(os.path.exists(os.path.join(package_path, 'conda',
            '{}.zip'.format(self.model.model_name))), False)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    @mock.patch('oml.util.pipeline.get_pipeline_owner')
    @mock.patch('oml.context.Context.is_outdated')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.update_deployment')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.create_deployment')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.register')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.get_model')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.get_model_artifacts')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.get_model_deployments')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.get_model_tests')
    @mock.patch('oml.hooks.dlis.DLISHook.get_active_models')
    @mock.patch('oml.hooks.dlis.DLISHook.create_deployment')
    @mock.patch('oml.hooks.dlis.DLISHook.get_deployments')
    @mock.patch('oml.hooks.dlis.DLISHook.get_tests')
    @mock.patch('oml.hooks.dlis.DLISHook.create_test')
    @mock.patch('subprocess.run')
    @mock.patch('oml.util.auth.get_token')
    def test_dlis_python_deployment_params(self, mock_get_token, mock_run, mock_create_test, mock_get_tests,
            mock_get_deployments, mock_deployment, mock_get_models, mock_get_model_tests,
            mock_get_model_deployments, mock_get_model_artifacts, mock_get_model, mock_register,
            mock_create_deployment, mock_update_deployment, mock_outdated, mock_pipeline_owner):
        mock_get_token.return_value = {'accessToken': '1111'}
        artifact_path = 'https://path/to/model/'
        mock_get_model.return_value = {
            'id': '1',
            'owner': 'test\\test',
            'name': 'test',
            'language': PYTHON_LANG,
        }
        mock_pipeline_owner.return_value = 'domain\\name'
        mock_get_model_artifacts.return_value = [{
            'id': '1',
            'path': artifact_path,
            'is_compliant': False
        }]
        mock_get_model_tests.return_value = [{
            'job_id': '1'
        }]
        mock_get_model.return_value.update({'namespace': {'name': 'test'}})
        mock_create_test.return_value = 'test'
        mock_get_tests.return_value = {
            'Status': 'Succeeded'
        }
        mock_deployment.return_value = 'deploy'
        mock_get_deployments.return_value = [{
            'ModelVersion': 1
        }]
        # Non-compliant deployment
        result = CliRunner().invoke(main, ['dlis', 'deploy', '-ns', 'test'])
        self.assertEqual(result.exit_code, 0)
        args, kwargs = mock_deployment.call_args
        self.assertEqual(args[0]["ModelPath"]["CosmosPath"], artifact_path + "model/run.cmd")
        self.assertEqual(args[0]["CondaPath"]["CosmosPath"], artifact_path + "conda/test.zip")
        self.assertIn('Task submitted', result.output)

        # Compliant deployment
        result = CliRunner().invoke(main, ['-v', 'dlis', 'deploy', '-c', '-t', '1234', '-ns', 'test'])
        self.assertEqual(result.exit_code, 0)
        args, kwargs = mock_deployment.call_args
        self.assertEqual(args[0]["ModelPath"]["AzurePath"], artifact_path + "model/run.cmd")
        self.assertEqual(args[0]["CondaPath"]["AzurePath"], artifact_path + "conda/test.zip")
        self.assertIn('Task submitted', result.output)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    @mock.patch('shutil.rmtree')
    @mock.patch('subprocess.run')
    def test_manifest(self, mock_subprocess, mock_rmtree):
        conda_package_path = os.path.join(self.tmp_dirpath, '.oml', 'env', self.model.model_name)
        os.makedirs(conda_package_path, exist_ok=True)
        self.model.package('dlis', skip_archive=True)
        self.model.create_manifests()
        model_manifest_path = os.path.join(self.tmp_dirpath, '.oml', 'package', 'model', 'SecureManifest.json')
        conda_manifest_path = os.path.join(conda_package_path, 'SecureManifest.json')
        self.assertEqual(os.path.exists(model_manifest_path), True)
        self.assertEqual(os.path.exists(conda_manifest_path), True)
