import os
import sys
import tempfile

from click.testing import CliRunner
from oml.cli import main
from oml.factory import TemplateFactory
from oml.util.os import touch
from oml.settings import load_model_metadata, find_base_path, update_model_metadata, PYTHON_LANG
from unittest import mock, skipUnless, TestCase

TIMEOUT = 200
NAMESPACE = 'test'
INSTANCES = 5
CORES = 8
MEMORY = 2048


class DLISConfigTest(TestCase):

    def setUp(self):
        self.tmp_dirpath = tempfile.mkdtemp()
        factory = TemplateFactory(PYTHON_LANG)
        factory.generate(self.tmp_dirpath, 'scikit-learn')
        os.chdir(self.tmp_dirpath)
        os.makedirs(os.path.join('.oml', 'package'), exist_ok=True)
        touch(os.path.join('.oml', 'package', 'file.txt'))

        # Update oml.yml
        base_path = find_base_path(self.tmp_dirpath)
        metadata = load_model_metadata(base_path)
        metadata['commands'] = {
            'dlis':
            {'deploy':
                {'instances': INSTANCES,
                 'cpu-cores': CORES,
                 'memory-usage-in-mb': MEMORY,
                 'namespace': NAMESPACE,
                 'timeout-in-ms': TIMEOUT}}
        }
        update_model_metadata(base_path, metadata)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    @mock.patch('oml.util.pipeline.get_pipeline_owner')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.create_deployment')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.get_model')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.get_model_artifacts')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.get_model_deployments')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.get_model_tests')
    @mock.patch('oml.hooks.dlis.DLISHook.get_active_models')
    @mock.patch('oml.hooks.dlis.DLISHook.create_deployment')
    @mock.patch('oml.hooks.dlis.DLISHook.get_deployments')
    @mock.patch('oml.hooks.dlis.DLISHook.get_tests')
    @mock.patch('oml.util.auth.get_token')
    def test_dlis_deployment_from_config(
            self, mock_get_token, mock_get_tests, mock_get_deployments, mock_deployment, mock_get_models,
            mock_get_model_tests, mock_get_model_deployments, mock_get_model_artifacts, mock_get_model,
            mock_create_deployment, mock_pipeline_owner):
        mock_get_token.return_value = {'accessToken': '1111'}
        path = 'https://path/to/model/'
        mock_get_model.return_value = {
            'id': 1,
            'owner': 'test\\test',
            'name': 'test',
            'language': PYTHON_LANG
        }
        mock_get_model_artifacts.return_value = [{
            'id': '1',
            'path': path,
            'is_compliant': False
        }]
        mock_get_model_tests.return_value = [{
            'job_id': '1'
        }]
        mock_get_tests.return_value = {
            'Status': 'Succeeded'
        }
        mock_pipeline_owner.return_value = 'domain\\name'

        result = CliRunner().invoke(main, ['dlis', 'deploy'])
        self.assertEqual(result.exit_code, 0)

        args, kwargs = mock_deployment.call_args
        deployment_args = args[0]
        self.assertEqual(deployment_args['TimeoutInMs'], TIMEOUT)
        self.assertEqual(deployment_args['Namespace'], NAMESPACE)
        self.assertEqual(deployment_args['Environments'][0]['MinInstanceNum'], INSTANCES)
        self.assertEqual(deployment_args['Environments'][0]['MaxInstanceNum'], INSTANCES)
