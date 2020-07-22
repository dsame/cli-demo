from unittest import mock, TestCase

from oml.hooks.catalog import ModelCatalogHook
from oml.settings import CSHARP_LANG

METADATA_NAME = 'test_name'
METADATA_OWNER = 'test\\test'
METADATA_FLAVOR = 'test_flavor'
METADATA_PLATFORM = 'test_platform'


class ModelCatalogHookTest(TestCase):

    @mock.patch('oml.util.auth.get_token')
    def setUp(self, mock_get_token):
        mock_get_token.return_value = {'accessToken': '1111'}
        self.hook = ModelCatalogHook()
        self.hook.metadata = {
            'name': METADATA_NAME,
            'owner': METADATA_OWNER,
            'language': CSHARP_LANG,
            'flavor': {'name': METADATA_FLAVOR},
            'platform': METADATA_PLATFORM,
            'is_compliant': False
        }

    @mock.patch('oml.hooks.api.ApiHook.create_artifact')
    @mock.patch('oml.hooks.api.ApiHook.create_model')
    @mock.patch('oml.hooks.api.ApiHook.get_model')
    def test_register(self, mock_get_model, mock_create_model, mock_create_artifact):
        artifact_type = 'model'
        version = '1.0.0'
        path = 'path/to/model'
        storage = 'adls'
        model_id = '10'
        is_compliant = False
        mock_create_model.return_value = {'id': model_id}
        self.hook.register(artifact_type, version, path, storage, is_compliant)
        mock_create_model.assert_called_with({
            'flavor': METADATA_FLAVOR,
            'language': CSHARP_LANG,
            'owner': METADATA_OWNER,
            'name': METADATA_NAME
        })
        mock_create_artifact.assert_called_with({
            'model_id': model_id,
            'version': version,
            'type': artifact_type,
            'path': path,
            'storage': storage,
            'platform': METADATA_PLATFORM,
            'is_compliant': is_compliant
        })

    @mock.patch('oml.hooks.api.ApiHook.create_deployment')
    def test_create_deployment(self, mock_create_deployment):
        artifact_id = '1'
        job_id = '1234'
        job_type = 'test'
        self.hook.create_deployment(artifact_id, job_id, job_type)
        mock_create_deployment.assert_called_with({
            'status': 'queued',
            'job_id': job_id,
            'job_type': job_type,
            'artifact_id': artifact_id
        })

    @mock.patch('oml.hooks.api.ApiHook.update_deployment')
    def test_update_deployment(self, mock_update_deployment):
        self.hook.update_deployment(job_id='1234', status='succeeded')
        mock_update_deployment.assert_called_with('1234', 'succeeded')

    @mock.patch('oml.hooks.api.ApiHook.get_artifacts')
    def test_list(self, mock_get_artifacts):
        mock_get_artifacts.return_value = {
            'ID': '1'
        }
        self.hook.list()
        mock_get_artifacts.assert_called_with(name=METADATA_NAME)
        self.hook.list(model_name='model')
        mock_get_artifacts.assert_called_with(name='model')

    @mock.patch('oml.hooks.api.ApiHook.get_model')
    def test_get_model(self, mock_get_model):
        self.hook.get_model('test')
        mock_get_model.assert_called_with(name='test')

    @mock.patch('oml.hooks.api.ApiHook.get_artifacts')
    def test_get_model_artifacts(self, mock_get_artifacts):
        self.hook.get_model_artifacts('1', is_compliant=False, version='1.0.1')
        mock_get_artifacts.assert_called_with('1', False, '1.0.1')

    @mock.patch('oml.hooks.api.ApiHook.get_deployments')
    def test_get_model_deployments(self, mock_get_deployments):
        self.hook.get_model_deployments(artifact_id='1')
        mock_get_deployments.assert_called_with('1')

    @mock.patch('oml.hooks.api.ApiHook.get_tests')
    def test_get_model_tests(self, mock_get_tests):
        self.hook.get_model_tests(artifact_id='1')
        mock_get_tests.assert_called_with('1')
