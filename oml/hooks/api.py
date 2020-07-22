import requests

from oml.exceptions import OMLException
from oml.settings import API_ENDPOINT
from oml.util import auth
from oml.util.requests import handle_response


class ApiHook:

    def __init__(self):
        endpoint = '/'.join([API_ENDPOINT, 'api', 'v1'])
        self.models_url = '/'.join([endpoint, 'models'])
        self.artifacts_url = '/'.join([endpoint, 'artifacts'])
        self.deployments_url = '/'.join([endpoint, 'deployments'])
        token = auth.get_token(API_ENDPOINT)
        self._session = requests.Session()
        self._session.headers.update({'Authorization': 'Bearer {}'.format(token['accessToken'])})

    @handle_response
    def create_model(self, data):
        return self._session.post(self.models_url, json=data)

    @handle_response
    def get_model(self, id=None, name=None):
        if id is not None:
            return self._session.get('/'.join([self.models_url, id]))
        elif name is not None:
            return self._session.get(self.models_url, params={'name': name})

    @handle_response
    def list_models(self):
        return self._session.get(self.models_url)

    @handle_response
    def create_artifact(self, data):
        return self._session.post(self.artifacts_url, json=data)

    @handle_response
    def get_artifacts(self, model_id=None, is_compliant=None, version=None, name=None):
        if model_id is None and name is not None:
            models = self.get_model(name=name)
            model = next(iter(models), None)
            if model is not None:
                model_id = model['id']
            else:
                raise OMLException('No models were found with name {}'.format(name))
        elif model_id is None and name is None:
            raise OMLException('You need to provide either model id or name to get the artifacts.')
        url = '/'.join([self.models_url, '{}'.format(model_id), 'artifacts'])
        params = {}
        if is_compliant is not None:
            params.update({'is_compliant': is_compliant})
        if version is not None:
            params.update({'version': version})
        if name is not None:
            params.update({'name': name})
        return self._session.get(url, params=params)

    @handle_response
    def create_deployment(self, data):
        return self._session.post(self.deployments_url, json=data)

    @handle_response
    def get_deployment_jobs(self, job_type, artifact_id):
        if artifact_id is not None:
            url = '/'.join([self.artifacts_url, '{}'.format(artifact_id), 'deployments'])
        else:
            url = self.deployments_url
        params = {'job_type': job_type}
        return self._session.get(url, params=params)

    def get_tests(self, artifact_id):
        return self.get_deployment_jobs('test', artifact_id)

    def get_deployments(self, artifact_id):
        return self.get_deployment_jobs('deployment', artifact_id)

    @handle_response
    def update_deployment(self, job_id, status):
        return self._session.put(self.deployments_url, json={'status': status}, params={'job_id': job_id})
