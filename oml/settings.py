import os
import uuid
import yaml

from pathlib import Path


# PACKAGE RELATED PATHS
PACKAGE_BASE_PATH = os.path.dirname(__file__)

EXEC_BASE_PATH = os.path.join(PACKAGE_BASE_PATH, 'exec')

TEMPLATE_BASE_PATH = os.path.join(PACKAGE_BASE_PATH, 'templates')
TEMPLATE_COMMON_DIR_PATH = os.path.join(TEMPLATE_BASE_PATH, 'common')
TEMPLATE_LANG_DIR_PATH = os.path.join(TEMPLATE_BASE_PATH, 'languages')
TEMPLATE_PLATFORM_DIR_PATH = os.path.join(TEMPLATE_BASE_PATH, 'platforms')
TEMPLATE_ADDONS_DIR_PATH = os.path.join(TEMPLATE_BASE_PATH, 'addons')

# CONFIG FILE
conf_filename = 'conf.yml'
if os.environ.get('ENVIRONMENT') == 'dev':
    conf_filename = 'conf.dev.yml'
CONF_FILE_PATH = os.path.join(PACKAGE_BASE_PATH, os.path.join('conf', conf_filename))

# CACHE
APP_CACHE_DIR_PATH = os.path.join(os.path.expanduser('~'), '.oml')
ADLS_TOKEN_FILE_PATH = os.path.join(APP_CACHE_DIR_PATH, 'token.yml')
ADAL_TOKEN_FILE_PATH = os.path.join(APP_CACHE_DIR_PATH, 'accessTokens.json')
METADATA_FILE_PATH = os.path.join(APP_CACHE_DIR_PATH, 'metadata.yml')

MODEL_FILENAME = 'model.py'
MODEL_META_FILENAME = 'oml.yml'
SCORE_FILENAME = '.score'
PYTHON_LANG = 'python'
CSHARP_LANG = 'c#'
TEST_JOB_TYPE = 'test'
DEPLOYMENT_JOB_TYPE = 'deployment'

# Create local cache directory if not exists
if not os.path.exists(APP_CACHE_DIR_PATH):
    os.makedirs(APP_CACHE_DIR_PATH, exist_ok=True)

# Load UUID from local cache
USER_ID = None
if os.path.exists(METADATA_FILE_PATH):
    with open(METADATA_FILE_PATH, 'r') as f:
        metadata = yaml.safe_load(f)
        USER_ID = metadata['user_id']
else:
    USER_ID = str(uuid.uuid4())
    data = {'user_id': USER_ID}
    with open(METADATA_FILE_PATH, 'w') as f:
        yaml.dump(data, stream=f, default_flow_style=False)

# Load configurations from config file
with open(CONF_FILE_PATH, 'r') as f:
    cfg = yaml.safe_load(f)

CLIENT_ID = cfg['app']['omlcli-client-id']
TENANT_ID = cfg['app']['tenant-id']
AUTHORITY_URI = 'https://login.microsoftonline.com/' + TENANT_ID

MODEL_STORE_ADLS_NAME = cfg['azure']['data-lake-storage']['name']
DLIS_ADLS_MODEL_STORE = cfg['dlis']['model-store']['adls']['uri']
DLIS_ADLS_MODEL_STORE_NAME = cfg['dlis']['model-store']['adls']['store-name']
DLIS_COSMOS_ADLS_MODEL_STORE = cfg['dlis']['model-store']['cosmos-adls']['uri']
DLIS_COSMOS_ADLS_MODEL_STORE_NAME = cfg['dlis']['model-store']['cosmos-adls']['store-name']
DLIS_COSMOS_ADLS_MODEL_STORE_HTTP = cfg['dlis']['model-store']['cosmos-adls']['public']
DLIS_API_ENDPOINT = cfg['dlis']['api']['uri']
DLIS_COSMOS_MODEL_STORE = cfg['dlis']['model-store']['cosmos']['uri']['private']
DLIS_COSMOS_MODEL_STORE_HTTP = cfg['dlis']['model-store']['cosmos']['uri']['public']
GIT_REPOSITORY_URL = cfg['git-repository']['uri']
APP_INSIGHTS_KEY = cfg['azure']['application-insights']['instrumentation-key']
APP_INSIGHTS_EVENT_TITLE = cfg['azure']['application-insights']['event-title']
STORAGE_ENDPOINT = cfg['azure']['storage']['uri']
STORAGE_ACCOUNT = cfg['azure']['storage']['account']
API_ENDPOINT = cfg['azure']['api']['uri']


def find_base_path(path):
    pointer = Path(path)
    while True:
        if pointer == pointer.parent:
            return str(pointer)

        fi = pointer.joinpath(MODEL_META_FILENAME)
        if fi.exists():
            return str(pointer)
        else:
            pointer = pointer.parent


def load_model_metadata(base_path):
    try:
        path = os.path.join(base_path, MODEL_META_FILENAME)
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        raise FileExistsError('OML project not found.')


def update_model_metadata(base_path, metadata):
    path = os.path.join(base_path, MODEL_META_FILENAME)
    with open(path, 'w') as f:
        return yaml.dump(metadata, stream=f, default_flow_style=False)


def get_user_metadata():
    if os.path.exists(METADATA_FILE_PATH):
        with open(METADATA_FILE_PATH) as f:
            return yaml.safe_load(f)

    return dict()


def update_user_metadata(key, value):
    metadata = get_user_metadata()
    metadata[key] = value

    with open(METADATA_FILE_PATH, 'w') as f:
        yaml.dump(metadata, stream=f, default_flow_style=False)
