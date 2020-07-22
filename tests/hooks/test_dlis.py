from unittest import mock, TestCase
import responses

from oml.hooks.dlis import DLISHook
from oml.settings import DLIS_API_ENDPOINT


class DLISHookTest(TestCase):

    @mock.patch('oml.util.auth.get_token')
    def setUp(self, mock_get_token):
        mock_get_token.return_value = {'accessToken': '1111'}
        self.hook = DLISHook()
        self.dlis_endpoint = '/'.join([DLIS_API_ENDPOINT, 'dlis'])

    @responses.activate
    def test_get_tests(self):
        responses.add(responses.GET,
            '/'.join([self.dlis_endpoint, 'tests']),
            json=[{'ID': '0'}, {'ID': '1'}])
        responses.add(responses.GET,
            '/'.join([self.dlis_endpoint, 'tests', '1']),
            json={'ID': '1'})

        res = self.hook.get_tests()
        self.assertEqual(res, [{'ID': '0'}, {'ID': '1'}])
        res = self.hook.get_tests('1')
        self.assertEqual(res, {'ID': '1'})

    @responses.activate
    def test_create_test(self):
        responses.add(responses.POST,
            '/'.join([self.dlis_endpoint, 'tests']),
            json={'ID': '1'})

        res = self.hook.create_test(data={'test': 'test'})
        self.assertEqual(res, {'ID': '1'})

    @responses.activate
    def test_get_deployments(self):
        responses.add(responses.GET,
            '/'.join([self.dlis_endpoint, 'deployments']),
            json=[{'ID': '0'}, {'ID': '1'}])
        responses.add(responses.GET,
            '/'.join([self.dlis_endpoint, 'deployments', '1']),
            json={'ID': '1'})

        res = self.hook.get_deployments()
        self.assertEqual(res, [{'ID': '0'}, {'ID': '1'}])
        res = self.hook.get_deployments('1')
        self.assertEqual(res, {'ID': '1'})

    @responses.activate
    def test_create_deployment(self):
        responses.add(responses.POST,
            '/'.join([self.dlis_endpoint, 'deployments']),
            json={'ID': '1'})

        res = self.hook.create_deployment(data={'test': 'test'})
        self.assertEqual(res, {'ID': '1'})
