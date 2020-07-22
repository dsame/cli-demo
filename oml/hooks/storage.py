from azure.storage.common import TokenCredential
from azure.storage.blob import BlockBlobService
from oml.settings import STORAGE_ACCOUNT, STORAGE_ENDPOINT
from oml.util import auth


class AzureStorageHook:

    def __init__(self):
        # https://docs.microsoft.com/en-us/azure/storage/common/storage-auth-aad-app
        token = TokenCredential(auth.get_token(STORAGE_ENDPOINT))
        self.blob_service = BlockBlobService(STORAGE_ACCOUNT, token_credential=token['accessToken'])

    def upload(self, container_name, blob_name, local_file_path):
        if not self.blob_service.exists(container_name):
            self.blob_service.create_container(container_name)

        self.blob_service.create_blob_from_path(container_name, blob_name, local_file_path)

    def list_containers(self):
        return self.blob_service.list_containers()
