import time

from azure.datalake.store import core, lib, multithread
from oml.settings import CLIENT_ID, TENANT_ID
from oml.util import auth

DATALAKE = 'https://datalake.azure.net/'


class AzureDataLakeStoreHook:
    def __init__(self, store_name):
        print('Connecting to {}'.format(store_name))
        self.store_name = store_name
        self.authenticate()

    def authenticate(self):
        token = auth.get_token(DATALAKE)
        # Needed for ADLS datalake operations
        token.update({
            'access': token['accessToken'],
            'resource': DATALAKE,
            'refresh': token.get('refreshToken', False),
            'time': time.time(),
            'tenant': TENANT_ID,
            'client': CLIENT_ID
        })
        adlCreds = lib.DataLakeCredential(token)

        # Create a filesystem client object
        self.adls = core.AzureDLFileSystem(adlCreds, store_name=self.store_name)

    def upload(self, src, dest, overwrite=True):
        print('Uploading from {} to {}'.format(src, dest))
        multithread.ADLUploader(self.adls, dest, src, overwrite=overwrite)
        print('Uploaded!')
