import os
import sys
import tempfile

from click.testing import CliRunner
from oml.cli import main
from oml.factory import TemplateFactory
from oml.util.os import touch
from oml.settings import CSHARP_LANG
from unittest import mock, skipUnless, TestCase


class CLITest(TestCase):

    def setUp(self):
        self.tmp_dirpath = tempfile.mkdtemp()
        factory = TemplateFactory(CSHARP_LANG)
        factory.generate(self.tmp_dirpath, 'tensorflow', 'Release')
        os.chdir(self.tmp_dirpath)
        os.makedirs(os.path.join('.oml', 'package'), exist_ok=True)
        touch(os.path.join('.oml', 'package', 'file.txt'))

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    @mock.patch('oml.util.pipeline.get_pipeline_owner')
    @mock.patch('oml.hooks.adls.AzureDataLakeStoreHook.authenticate')
    @mock.patch('oml.hooks.adls.AzureDataLakeStoreHook.upload')
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
    @mock.patch('oml.util.auth.get_token')
    def test_dlis_deployment(self, mock_get_token, mock_create_test, mock_get_tests, mock_get_deployments,
            mock_deployment, mock_get_models, mock_get_model_tests, mock_get_model_deployments,
            mock_get_model_artifacts, mock_get_model, mock_register, mock_create_deployment, mock_update_deployment,
            mock_outdated, mock_adls_upload, mock_auth, mock_pipeline_owner):
        # Non-compliant deployment
        if 'BUILD_STAGINGDIRECTORY' in os.environ:
            os.environ.pop('BUILD_STAGINGDIRECTORY')
        path = 'https://path/to/model/'
        model_id = 1
        artifact_id = 1
        test_id = 1
        deployment_id = '1234'
        mock_get_token.return_value = {'accessToken': '1111'}
        mock_get_model.return_value = {
            'id': model_id,
            'owner': 'test\\test',
            'name': 'test',
            'language': CSHARP_LANG,
        }
        mock_get_model_artifacts.return_value = [{
            'id': artifact_id,
            'path': path,
            'is_compliant': False
        }]
        result = CliRunner().invoke(main, ['publish'])
        self.assertEqual(mock_adls_upload.call_count, 1)
        args, kwargs = mock_adls_upload.call_args
        self.assertIn('local/omlmodels', args[1])
        self.assertEqual(result.exit_code, 0)

        mock_get_model.return_value.update({'namespace': {'name': 'test'}})
        mock_create_test.return_value = 'test'
        mock_pipeline_owner.return_value = 'domain\\name'
        result = CliRunner().invoke(main, ['dlis', 'test'])
        self.assertEqual(result.exit_code, 0)
        mock_get_model_tests.return_value = [{
            'job_id': test_id
        }]
        mock_get_tests.return_value = {
            'Status': 'Succeeded'
        }
        result = CliRunner().invoke(main, ['dlis', 'show', '--id', test_id])
        self.assertEqual(result.exit_code, 0)
        mock_deployment.return_value = deployment_id
        mock_get_deployments.return_value = [{
            'ModelVersion': 1
        }]
        # When deploying, namespace must be specified or set in oml.yml
        result = CliRunner().invoke(main, ['dlis', 'deploy'])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Namespace is required', result.output)
        result = CliRunner().invoke(main, ['dlis', 'deploy', '-ns', 'test'])
        mock_get_model_artifacts.assert_called_with(model_id, is_compliant=None, version=None)
        mock_get_model_tests.assert_called_with(test_id)
        mock_create_deployment.assert_called_with(artifact_id, deployment_id, 'deployment')
        self.assertEqual(result.exit_code, 0)
        args, kwargs = mock_deployment.call_args
        self.assertEqual(args[0]["ModelPath"]["CosmosPath"], path)
        self.assertIn('Task submitted', result.output)

        # Compliant deployment
        os.environ['OML_CLI_KEY'] = '1234'
        os.environ['BUILD_STAGINGDIRECTORY'] = 'abcd'
        result = CliRunner().invoke(main, ['dlis', 'manifest'])
        self.assertEqual(result.exit_code, 0)

        result = CliRunner().invoke(main, ['publish'])
        self.assertEqual(mock_adls_upload.call_count, 2)
        args, kwargs = mock_adls_upload.call_args
        self.assertNotIn('local/omlmodels', args[1])
        self.assertEqual(result.exit_code, 0)
        mock_get_model_artifacts.return_value[0]['is_compliant'] = True

        result = CliRunner().invoke(main, ['dlis', 'deploy'])
        self.assertEqual(result.exit_code, 1)
        # When deploying, namespace must be specified or set in oml.yml
        result = CliRunner().invoke(main, ['-v', 'dlis', 'deploy', '-t', '1234'])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Namespace is required', result.output)
        result = CliRunner().invoke(main, ['-v', 'dlis', 'deploy', '-t', '1234', '-ns', 'test'])
        mock_get_model_artifacts.assert_called_with(model_id, is_compliant=None, version=None)
        self.assertEqual(result.exit_code, 0)
        args, kwargs = mock_deployment.call_args
        self.assertEqual(args[0]["ModelPath"]["AzurePath"], path.strip("/"))
        self.assertIn('Task submitted', result.output)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.update_deployment')
    @mock.patch('oml.hooks.catalog.ModelCatalogHook.get_model')
    @mock.patch('oml.hooks.dlis.DLISHook.get_tests')
    @mock.patch('oml.util.auth.get_token')
    def test_cli_dlis_list(self, mock_get_token, mock_get_tests, mock_get_model, mock_update_deployment):
        new_status = 'succeeded'
        test_id = '1234'
        mock_get_token.return_value = {'accessToken': '1111'}
        mock_get_model.return_value = {
            'owner': 'REDMOND\\test',
            'name': 'test'
        }
        mock_get_tests.return_value = [{
            'ID': test_id,
            'ModelName': 'test',
            'StartTime': 'test',
            'EndTime': 'test',
            'Status': new_status,
            'Error': 'test'
        }]
        result = CliRunner().invoke(main, ['dlis', 'list'])
        mock_update_deployment.assert_called_with(test_id, new_status)
        self.assertEqual(mock_get_tests.call_count, 1)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('1 test(s) found', result.output)
