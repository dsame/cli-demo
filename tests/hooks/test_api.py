from unittest import mock, TestCase
from requests import ConnectionError
import responses

from oml.hooks.api import ApiHook
from oml.exceptions import OMLException


class ApiHookTest(TestCase):

    @mock.patch('oml.util.auth.get_token')
    def setUp(self, mock_get_token):
        mock_get_token.return_value = {'accessToken': '1111'}
        self.hook = ApiHook()

    @responses.activate
    def test_create_model(self):
        responses.add(responses.POST,
            self.hook.models_url,
            json={'ID': '1'})

        res = self.hook.create_model(data={'test': 'test'})
        self.assertEqual(res, {'ID': '1'})

    @responses.activate
    def test_get_model(self):
        responses.add(responses.GET,
            '/'.join([self.hook.models_url, '1']),
            json={'ID': '1'})

        res = self.hook.get_model('1')
        self.assertEqual(res, {'ID': '1'})

    @responses.activate
    def test_list_models(self):
        responses.add(responses.GET,
            self.hook.models_url,
            json=[{'ID': '0'}, {'ID': '1'}])

        res = self.hook.list_models()
        self.assertEqual(res, [{'ID': '0'}, {'ID': '1'}])

    @responses.activate
    def test_create_artifact(self):
        responses.add(responses.POST,
            self.hook.artifacts_url,
            json={'ID': '1'})

        res = self.hook.create_artifact(data={'test': 'test'})
        self.assertEqual(res, {'ID': '1'})

    @responses.activate
    def test_get_artifacts(self):
        # TODO: ADD PARAMS CHECK
        responses.add(responses.GET,
            '/'.join([self.hook.models_url, '1']),
            json={'id': '1', 'name': 'test1'})
        responses.add(responses.GET,
            '{}?name={}'.format(self.hook.models_url, 'test2'),
            match_querystring=True,
            json=[{'id': '2', 'name': 'test2'}])
        responses.add(responses.GET,
            '{}?name={}'.format(self.hook.models_url, 'nonexistent'),
            match_querystring=True,
            status=404)

        responses.add(responses.GET,
            '/'.join([self.hook.models_url, '1', 'artifacts']),
            json={'ID': '4'})
        responses.add(responses.GET,
            '/'.join([self.hook.models_url, '2', 'artifacts']),
            json={'ID': '5'})

        res = self.hook.get_artifacts(model_id='1')
        self.assertEqual(res, {'ID': '4'})
        res = self.hook.get_artifacts(name='test2')
        self.assertEqual(res, {'ID': '5'})
        with self.assertRaises(ConnectionError):
            self.hook.get_artifacts('nonexistent')
        with self.assertRaises(OMLException):
            self.hook.get_artifacts()

    @responses.activate
    def test_create_deployment(self):
        responses.add(responses.POST,
            self.hook.deployments_url,
            json={'ID': '1'})

        res = self.hook.create_deployment(data={'test': 'test'})
        self.assertEqual(res, {'ID': '1'})

    @responses.activate
    def test_get_tests(self):
        # TODO: ADD PARAMS CHECK
        responses.add(responses.GET,
            '/'.join([self.hook.artifacts_url, '1', 'deployments']),
            json={'ID': '1'})
        responses.add(responses.GET,
            self.hook.deployments_url,
            json={'ID': '2'})

        res = self.hook.get_tests(artifact_id='1')
        self.assertEqual(res, {'ID': '1'})
        res = self.hook.get_tests(artifact_id=None)
        self.assertEqual(res, {'ID': '2'})

    @responses.activate
    def test_get_deployments(self):
        # TODO: ADD PARAMS CHECK
        responses.add(responses.GET,
            '/'.join([self.hook.artifacts_url, '1', 'deployments']),
            json={'ID': '1'})
        responses.add(responses.GET,
            self.hook.deployments_url,
            json={'ID': '2'})

        res = self.hook.get_deployments(artifact_id='1')
        self.assertEqual(res, {'ID': '1'})
        res = self.hook.get_deployments(artifact_id=None)
        self.assertEqual(res, {'ID': '2'})

    @responses.activate
    def test_update_deployment(self):
        responses.add(responses.PUT,
            self.hook.deployments_url,
            json={'ID': '1'})

        res = self.hook.update_deployment(job_id='1234', status='succeeded')
        self.assertEqual(res, {'ID': '1'})
