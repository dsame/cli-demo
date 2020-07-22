import requests

from oml.exceptions import OMLException
from oml.settings import API_ENDPOINT, DLIS_API_ENDPOINT
from oml.util import auth


class DLISHook:

    def __init__(self):
        self.tests_url = '/'.join([DLIS_API_ENDPOINT, 'dlis', 'tests'])
        self.deployments_url = '/'.join([DLIS_API_ENDPOINT, 'dlis', 'deployments'])
        self.active_models_url = '/'.join([DLIS_API_ENDPOINT, 'dlis', 'activemodels'])
        token = auth.get_token(API_ENDPOINT)
        self._session = requests.Session()
        self._session.headers.update({'Authorization': 'Bearer {}'.format(token['accessToken'])})

    def get_tests(self, id=None, filter=None):
        if filter is not None:
            filter = self._get_odata_filter(filter)
        else:
            filter = {'$orderby': 'StartTime desc'}

        if id is None:
            res = self._session.get(self.tests_url, params=filter)
        else:
            res = self._session.get('/'.join([self.tests_url, id]))
        if res.status_code == 200:
            return res.json()
        else:
            self._raise_exception_with_suggestions(res)

    def create_test(self, data):
        res = self._session.post(self.tests_url, json=data)
        if res.status_code == 200:
            return res.json()
        else:
            self._raise_exception_with_suggestions(res)

    def get_deployments(self, id=None, filter=None):
        if filter is not None:
            filter = self._get_odata_filter(filter)
        else:
            filter = {'$orderby': 'StartTime desc'}

        if id is None:
            res = self._session.get(self.deployments_url, params=filter)
        else:
            res = self._session.get('/'.join([self.deployments_url, id]))

        if res.status_code == 200:
            return res.json()
        else:
            self._raise_exception_with_suggestions(res)

    def create_deployment(self, data):
        res = self._session.post(self.deployments_url, json=data)

        if res.status_code == 200:
            return res.json()
        else:
            self._raise_exception_with_suggestions(res)

    def get_active_models(self, filter=None, namespace=None, name=None):
        if filter is not None:
            filter = self._get_odata_filter(filter)

        if namespace is None or name is None:
            res = self._session.get(self.active_models_url, params=filter)
        else:
            res = self._session.get('/'.join([self.active_models_url, '{}.{}'.format(namespace, name)]), params=filter)

        if res.status_code == 200:
            return res.json()
        else:
            self._raise_exception_with_suggestions(res)

    @staticmethod
    def _get_odata_filter(filter):
        where = []
        for k, v in filter.items():
            if type(v) == bool:
                where.append("{} eq {}".format(k, str(v).lower()))
            else:
                where.append("{} eq '{}'".format(k, v))
        return {'$filter': ' and '.join(where), '$orderby': 'StartTime desc'}

    def _raise_exception_with_suggestions(self, res):
        suggestion = 'HINT: '
        if ('Must specify a legal namespace' in res.text):
            suggestion += 'Check that you are listed as a namespace admin in the OS Portal ' \
                '(http://osportal.binginternal.com/Partner/Index) in DOMAIN\\alias format. If this is a new ' \
                'namespace, it also needs to be enabled for use by OML tool in the DLIS side. Please fill in the ' \
                'following task http://aka.ms/DLISDRIAsk and specify that you need your namespace enabled for use ' \
                'by the OML tool. '
        if ('already exists in at least one enviroment' in res.text):
            suggestion += 'Try adding the parameter "--force-replace" to the deploy command.'
        raise OMLException('{} {} {} \n\n{}'.format(res.status_code, res.reason, res.text, suggestion))
