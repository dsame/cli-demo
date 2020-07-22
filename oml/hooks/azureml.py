import base64
import json
import rsa
import yaml

from azureml.core.environment import Environment
from azureml.core import Workspace
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.core.model import InferenceConfig, Model
from azureml.contrib.mir.webservice import MirWebservice
from azureml.core.webservice import Webservice
from azureml.exceptions import WebserviceException
from oml.exceptions import OMLException


class AzureMlHook:

    def __init__(self):
        self.auth = InteractiveLoginAuthentication()

    def get_identity(self):
        return AdalIdentity(self.auth)

    def get_workspace(self, workspace_name, resource_group, subscription_id):
        return Workspace.get(workspace_name,
                             auth=self.auth,
                             resource_group=resource_group,
                             subscription_id=subscription_id)

    def create_workspace(self,
                         workspace_name,
                         location,
                         resource_group,
                         subscription_id,
                         container_registry=None,
                         app_insights=None):
        return Workspace.create(
            workspace_name,
            auth=self.auth,
            subscription_id=subscription_id,
            location=location,
            resource_group=resource_group,
            create_resource_group=True,
            app_insights=app_insights,
            container_registry=container_registry)

    def deploy(self,
               workspace_name,
               resource_group,
               subscription_id,
               model_name,
               service_name,
               inference_config_file,
               deployment_config_file,
               signing_certificate,
               overwrite,
               verbose):

        ws = Workspace.get(workspace_name,
                           auth=self.auth,
                           resource_group=resource_group,
                           subscription_id=subscription_id)
        inference_config = file_to_inference_config(ws, inference_config_file, description='')

        # Package the model so we have an immutable image url (using hash) to validate later
        models = Model.list(ws, model_name, latest=True)
        if len(models) == 0:
            raise OMLException("Model is not registered")
        if verbose:
            print("Packaging model.")
        model_package = Model.package(ws, [models[0].id], inference_config)
        model_package.wait_for_creation()
        image_uri = model_package.location
        if verbose:
            print("Model package generated at {}.".format(image_uri))

        # Generate a signature containing the immutable model image url
        if verbose:
            print("Generating deployment signature.")
        signature_payload = "imageUrl:{}".format(image_uri)
        signature_bytes = rsa.sign(signature_payload.encode('utf-8'), signing_certificate, 'SHA-384')
        signature = base64.b64encode(signature_bytes).decode('utf-8')

        # Set up base-image-only deploy configuration
        if verbose:
            print("Creating byoc inference config and deployment config.")
        # "AzureML-" is a reserved environment name prefix. Uniquify the environment name if using
        # a curated environment for this model.
        if inference_config.environment.name.startswith("AzureML-"):
            deploy_environment_name = "Office-{}-deploy".format(inference_config.environment.name[8:])
        else:
            deploy_environment_name = "{}-deploy".format(inference_config.environment.name)
        byoc_config = InferenceConfig(entry_script=inference_config.entry_script,
                                      environment=Environment(deploy_environment_name))
        byoc_config.environment.docker.base_image = image_uri
        byoc_config.environment.python.user_managed_dependencies = True
        properties = {
            "isByoc": "true",
            "requestSignaturePayload": signature_payload,
            "requestSignature": signature
        }
        deployment_config = file_to_deploy_config(deployment_config_file, properties)

        # MirWebservice doesn't support service updates.
        # Make sure you remove any existing service under the same name before calling deploy.
        if overwrite:
            if verbose:
                print("Deleting webservice if it exists.")
            try:
                Webservice(ws, service_name).delete()
                if verbose:
                    print("Previous webservice deleted.")
            except WebserviceException:
                pass

        if verbose:
            print("Deploying model.")
        service = Model.deploy(ws, service_name, models, byoc_config, deployment_config)
        try:
            service.wait_for_deployment()
        except WebserviceException:
            print('Failed service operation id: {}'.format(Webservice._get(ws, service_name)['operationId']))
            raise

        print("ScoringUri:{}\n".format(service.scoring_uri))
        return service


# Copied/adapted from AzureML SDK private APIs
def file_to_inference_config(workspace, inference_config_file, description):
    with open(inference_config_file) as inference_file_stream:
        inference_config_obj = file_stream_to_object(inference_file_stream)

        # Retrieve Environment object from the name in the InferenceConfig file
        if 'environment' not in inference_config_obj:
            raise OMLException("need to specify environment in --deploy-config-file")
        environment_name = inference_config_obj.get('environment')["name"]
        environment = Environment.get(workspace, name=environment_name)

        inference_config = InferenceConfig(
            entry_script=inference_config_obj.get('entryScript'),
            runtime=inference_config_obj.get('runtime'),
            conda_file=inference_config_obj.get('condaFile'),
            extra_docker_file_steps=inference_config_obj.get('extraDockerfileSteps'),
            source_directory=inference_config_obj.get('sourceDirectory'),
            enable_gpu=inference_config_obj.get('enableGpu'),
            base_image=inference_config_obj.get('baseImage'),
            base_image_registry=inference_config_obj.get('baseImageRegistry'),
            cuda_version=inference_config_obj.get('cudaVersion'),
            environment=environment,
            description=description)
        return inference_config


def file_to_deploy_config(deploy_config_file, properties):
    with open(deploy_config_file, 'r') as deploy_file_stream:
        deploy_config_obj = file_stream_to_object(deploy_file_stream)
        if 'computeType' not in deploy_config_obj:
            raise OMLException("need to specify computeType in --deployment-config-file")
        if deploy_config_obj['computeType'].lower() != 'mirsinglemodel':
            raise OMLException("computeType in --deploy-config-file must be 'MIRSINGLEMODEL'")

        return MirWebservice.deploy_configuration(
            autoscale_enabled=deploy_config_obj.get('autoscaler', {}).get('autoscaleEnabled'),
            autoscale_min_replicas=deploy_config_obj.get('autoscaler', {}).get('minReplicas'),
            autoscale_max_replicas=deploy_config_obj.get('autoscaler', {}).get('maxReplicas'),
            sku=deploy_config_obj.get('sku'),
            num_replicas=deploy_config_obj.get('numReplicas'),
            cpu_cores=deploy_config_obj.get('containerResourceRequirements', {}).get('cpu'),
            gpu_cores=deploy_config_obj.get('containerResourceRequirements', {}).get('gpu'),
            memory_gb=deploy_config_obj.get('containerResourceRequirements', {}).get('memoryInGB'),
            properties=properties,
            tls_mode="SIMPLE")


def file_stream_to_object(file_stream):
    """Expects a YAML or JSON file_stream and returns the file object
    :param file_stream: File stream from with open(file) as file_stream
    :type file_stream:
    :return: File dictionary
    :rtype: dict
    """
    file_data = file_stream.read()

    try:
        return yaml.safe_load(file_data)
    except yaml.YAMLError:
        pass

    try:
        return json.loads(file_data)
    except Exception:
        raise OMLException('Error while parsing file. Must be valid JSON or YAML file.')


# TODO: Replace this with better auth

class AdalIdentity:
    def __init__(self, aml_auth):
        self.token = aml_auth._get_arm_token_using_interactive_auth(resource="https://vault.azure.net")

    def get_token(self, _):
        return AdalToken(self.token)


class AdalToken:
    def __init__(self, token):
        self.token = token
