from oml.exceptions import OMLException
from oml.hooks.api import ApiHook


class ModelCatalogHook:

    def __init__(self, metadata=None, verbose=False):
        self.metadata = metadata
        self.api = ApiHook()

    def register(self, artifact_type, version, path, storage, is_compliant=False):
        if self.metadata is None:
            raise OMLException('Metadata not found.')

        model_data = {
            'name': self.metadata['name'],
            'owner': self.metadata['owner'],
            'language': self.metadata['language'],
            'flavor': self.metadata['flavor']['name']
        }

        model = self.get_model(name=model_data['name'])

        if model is None:
            new_model = self.api.create_model(model_data)
            model_id = new_model['id']
        else:
            model_id = model['id']

        artifact_data = {
            'model_id': model_id,
            'version': version,
            'type': artifact_type,
            'path': path,
            'storage': storage,
            'platform': self.metadata['platform'],
            'is_compliant': is_compliant
        }
        self.api.create_artifact(artifact_data)

    def create_deployment(self, artifact_id, job_id, job_type, status='queued'):
        """Tracking model deployment workflow.

        :param artifact_id: model's artifact id
        :param job_id: Platform API job id
        :param job_type: Type of jobs. Allowed values: 'test' and 'deployment'
        :param status: Job status. Allowed values: 'queued', 'running', 'failed', and 'succeeded'
        """

        deployment_data = {
            'artifact_id': artifact_id,
            'job_id': job_id,
            'job_type': job_type,
            'status': status
        }
        self.api.create_deployment(deployment_data)

    def update_deployment(self, job_id, status):
        self.api.update_deployment(job_id, status)

    def list(self, model_name=None):
        if model_name is None:
            model_name = self.metadata['name']

        return self.api.get_artifacts(name=model_name)

    def get_model(self, name):
        models = self.api.get_model(name=name)
        return next(iter(models), None)

    def get_model_artifacts(self, model_id, is_compliant=None, version=None):
        return self.api.get_artifacts(model_id, is_compliant, version)

    def get_model_deployments(self, artifact_id=None):
        return self.api.get_deployments(artifact_id)

    def get_model_tests(self, artifact_id=None):
        return self.api.get_tests(artifact_id)
