import os
import pkg_resources
import requests
import shutil
import uuid

from requests.exceptions import ConnectionError

from oml.exceptions import OMLException
from oml.hooks.catalog import ModelCatalogHook
from oml.hooks.adls import AzureDataLakeStoreHook
from oml.models.csharp import CSharpModel
from oml.models.python import PythonModel
from oml.settings import (
    load_model_metadata,
    update_model_metadata,
    DLIS_ADLS_MODEL_STORE,
    DLIS_ADLS_MODEL_STORE_NAME,
    DLIS_COSMOS_ADLS_MODEL_STORE_NAME,
    DLIS_COSMOS_ADLS_MODEL_STORE_HTTP,
    MODEL_META_FILENAME,
    PYTHON_LANG,
    CSHARP_LANG)
from oml.settings import find_base_path
from oml.util.version import increment
from oml.util.pipeline import is_running_in_pipeline


class Model:

    def __init__(self, path, verbose=False):
        self.base_path = find_base_path(path)
        self.metadata = load_model_metadata(self.base_path)
        self.language = self.metadata['language']
        self.model_name = self.metadata['name']
        self.model_version = self.metadata['version']
        self.owner = self.metadata['owner']
        self.tmp_dir_path = os.path.join(self.base_path, '.oml')
        self.inference_dir_path = os.path.join(self.tmp_dir_path, 'inference')
        self.package_dir_path = os.path.join(self.tmp_dir_path, 'package')
        self.proj_dir_path = os.path.join(self.base_path, self.model_name)

        self.model = self._load_model()
        self.verbose = verbose

    def list_artifacts(self, model_name):
        catalog = ModelCatalogHook(self.metadata)
        return catalog.list(model_name)

    def eval(self):
        self.model.eval()

    def serve(self, port=8000):
        self.model.serve(port)

    def test(
            self,
            mode='offline',
            path=None,
            delimiter='\t',
            endpoint='http://localhost:8000',
            verbose=False):
        if mode == 'live':
            counter = 0
            err = []
            is_ok = True
            if path is not None and not os.path.exists(path):
                raise FileExistsError('File not found.')

            with open(path, 'r') as f:
                for line in f:
                    result = ''
                    counter += 1
                    input, output = line.strip().split(delimiter)

                    try:
                        r = requests.post(endpoint, input)
                        result = r.text
                    except ConnectionError:
                        err.append('[Error] Failed to connect {}'.format(endpoint))
                        is_ok = False
                        break

                    if output != result:
                        err.append('[Error] Line {}: Expected={} Actual={}'.format(counter, output, result))
                        is_ok = False
            if is_ok:
                print('{} test executed: PASSED.'.format(counter))
            else:
                print('{} test executed: FAILED.'.format(counter))
                if verbose:
                    for e in err:
                        print(e)
        elif mode == 'offline':
            self.model.test()

    def package(self, platform, skip_archive):
        try:
            if os.path.exists(self.tmp_dir_path):
                shutil.rmtree(self.tmp_dir_path)
        except os.error as e:
            if('The directory is not empty' in e.strerror or 'Access is denied' in e.strerror):
                raise OMLException(e.strerror + ': ' + e.filename + '\nPlease close all file explorer windows, '
                    'files, processes or IDEs that might be using .oml/ or a python process and retry.')
            else:
                raise e
        platform = platform or self.metadata['platform'] or 'dlis'
        self.model.package(platform, skip_archive)

        # Update and copy metadata
        self.metadata['platform'] = platform
        update_model_metadata(self.base_path, self.metadata)
        self.model.copy_metadata(MODEL_META_FILENAME)

    def publish(self, storage, datasource_id=None, version=None,
            increment_type='patch', is_compliant=None):
        if version is None:
            version = self.model_version

        if not os.path.exists(self.package_dir_path):
            raise FileExistsError('Package folder not found. Please run "oml package" before publishing.')

        # Add oml version to metadata before publish
        self.metadata['oml-version'] = pkg_resources.require("oml")[0].version
        update_model_metadata(self.base_path, self.metadata)

        # If no flag was passed to force an option, check whether oml is running locally or in Azure pipeline
        if is_compliant is None:
            is_compliant = is_running_in_pipeline()
        if is_compliant or storage == 'adls':
            storage = 'adls'
            is_compliant = True
            dest_base_uri = self._publish_dlis_adls(version)
        else:
            storage = 'cosmos'
            is_compliant = False
            dest_base_uri = self._publish_cosmos_adls(version)

        catalog = ModelCatalogHook(self.metadata)
        catalog.register('model', version, dest_base_uri, storage, is_compliant)
        print('\nPublished version: {} to {}'.format(version, storage))

        # Update metadata
        self.metadata['version'] = increment(version, increment_type)
        update_model_metadata(self.base_path, self.metadata)

    def create_manifests(self):
        self.model.create_manifests()

    def _publish_dlis_adls(self, version):
        if not self.model.check_manifest_exists():
            raise FileExistsError('Manifest not found. Please run "oml dlis manifest" before publishing.')

        unique_id = str(uuid.uuid4())[:5]
        dest = '{}/{}/{}/{}'.format('models', self.model_name, version, unique_id)
        self._publish_adls(DLIS_ADLS_MODEL_STORE_NAME, dest)
        return '{}/{}/'.format(DLIS_ADLS_MODEL_STORE, dest)

    def _publish_cosmos_adls(self, version):
        unique_id = str(uuid.uuid4())[:5]
        dest = '{}/{}/{}/{}/{}'.format('local', 'omlmodels', self.model_name, version, unique_id)
        self._publish_adls(DLIS_COSMOS_ADLS_MODEL_STORE_NAME, dest)
        # We upload to ADLS behind DLIS Cosmos store, but we return the Cosmos path for accessing it later
        return '{}/{}/'.format(DLIS_COSMOS_ADLS_MODEL_STORE_HTTP, dest)

    def _publish_adls(self, store_name, dest):
        try:
            adls = AzureDataLakeStoreHook(store_name)
            adls.upload(self.package_dir_path, dest)
        except OMLException as e:
            raise OMLException('Something is wrong. ADLS upload failed. Error details: {}'.format(e))

    def _load_model(self):
        if self.language == PYTHON_LANG:
            return PythonModel(
                self.model_name,
                self.model_version,
                self.base_path,
                self.tmp_dir_path,
                self.package_dir_path,
                self.proj_dir_path)
        elif self.language == CSHARP_LANG:
            return CSharpModel(
                self.model_name,
                self.base_path,
                self.tmp_dir_path,
                self.inference_dir_path,
                self.package_dir_path,
                self.proj_dir_path,
                self.metadata)
