import rsa
import uuid

from azureml.exceptions import AzureMLException
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from oml.exceptions import OMLException
from oml.hooks.azureml import AzureMlHook
from oml.hooks.containerregistry import ContainerRegistryHook
from oml.hooks.keyvault import KeyVaultHook
from OpenSSL import crypto

acr_resource_id_format = "/subscriptions/{}/resourcegroups/{}/providers/microsoft.containerregistry/registries/{}"


class AzureMlApi:

    def __init__(self):
        self.client = AzureMlHook()
        self.acr = ContainerRegistryHook()
        self.keyvault = KeyVaultHook()

    def create_workspace(self, workspace, regions, resource_group, subscription_id, primary_workspace_name=None):
        if workspace is None:
            raise OMLException('Workspace name is empty.')
        if regions is None:
            raise OMLException('Regions is empty.')
        if subscription_id is None:
            raise OMLException('Subscription id is empty.')

        if resource_group is None:
            resource_group = 'aml-rg-{}'.format(workspace)

        region_list = list(map(lambda s: s.strip(), regions.split(',')))

        primary_workspace = None
        if primary_workspace_name is None:
            workspace_name = '{}-{}'.format(workspace, region_list[0])[:33]

            acr_name = _get_name_for_resource(workspace_name, 'acr')
            print("Creating shared container registry")
            print("Deploying ContainerRegistry with name {}.".format(acr_name))
            adal = self.client.auth._get_adal_auth_object()
            self.acr.create_registry(adal,
                                     acr_name,
                                     resource_group,
                                     region_list[0],
                                     subscription_id,
                                     admin_user_enabled=True)
            print("Deployed ContainerRegistry with name {}.".format(acr_name))
            acr_resource_id = acr_resource_id_format.format(subscription_id, resource_group, acr_name)

            print("Creating workspace {}".format(workspace_name))
            try:
                primary_workspace = self.client.create_workspace(workspace_name,
                                                                 region_list[0],
                                                                 resource_group,
                                                                 subscription_id,
                                                                 container_registry=acr_resource_id)
            except AzureMLException:
                self.acr.delete_registry(adal, acr_name, resource_group, subscription_id)
                raise

            region_list = region_list[1:]
        else:
            primary_workspace = self.client.get_workspace(primary_workspace_name, resource_group, subscription_id)

        details = primary_workspace.get_details()
        container_registry = details["containerRegistry"]
        app_insights = details["applicationInsights"]

        for region in region_list:
            workspace_name = '{}-{}'.format(workspace, region)[:33]
            print("Creating workspace {}".format(workspace_name))
            self.client.create_workspace(workspace_name,
                                         region,
                                         resource_group,
                                         subscription_id,
                                         container_registry,
                                         app_insights)

    def generate_fingerprint(self,
                             certificate_file,
                             certificate_url):
        if certificate_url is not None:
            identity = self.client.get_identity()
            private_key_bytes = self.keyvault.get_private_key(certificate_url, credentials=identity)
        else:
            with open(certificate_file, 'rb') as f:
                private_key_bytes = f.read()

        try:
            # Try loding the file as PEM
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, private_key_bytes)
        except crypto.Error:
            # File is PFX, load in pkcs12 format
            p12 = crypto.load_pkcs12(private_key_bytes)
            cert = p12.get_certificate()

        return cert.digest("sha256").decode('utf-8').replace(':', '')

    def deploy(self,
               workspace,
               resource_group,
               subscription_id,
               model_name,
               service_name,
               inference_config_file,
               deployment_config_file,
               signing_certificate_file,
               signing_certificate_url,
               overwrite,
               verbose):
        if signing_certificate_url is None and signing_certificate_file is None:
            raise OMLException('Both signing certificate file and url are empty.')

        if verbose:
            print("Loading signing certificate.")
        if signing_certificate_url is not None:
            identity = self.client.get_identity()
            private_key_bytes = self.keyvault.get_private_key(signing_certificate_url, credentials=identity)
            signing_cert = _convert_private_key_to_rsa(private_key_bytes)
        else:
            with open(signing_certificate_file, 'rb') as f:
                signing_cert = _convert_private_key_to_rsa(f.read())
        if verbose:
            print("Signing certificate loaded.")

        return self.client.deploy(workspace,
                                  resource_group,
                                  subscription_id,
                                  model_name,
                                  service_name,
                                  inference_config_file,
                                  deployment_config_file,
                                  signing_cert,
                                  overwrite,
                                  verbose)


def _get_name_for_resource(workspace_name, resource_type):
    alphabets_str = ""
    for char in workspace_name.lower():
        if char.isalpha() or char.isdigit():
            alphabets_str = alphabets_str + char
    rand_str = str(uuid.uuid4()).replace("-", "")
    resource_name = alphabets_str[:8] + resource_type[:8] + rand_str

    return resource_name[:24]


def _convert_private_key_to_rsa(data):
    try:
        return rsa.PrivateKey.load_pkcs1(data)
    except ValueError:
        pass

    p12 = crypto.load_pkcs12(data)
    pkey = p12.get_privatekey()
    crypto_key = pkey.to_cryptography_key()
    rsa_data = crypto_key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption())
    return rsa.PrivateKey.load_pkcs1(rsa_data)
