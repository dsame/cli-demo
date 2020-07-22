import base64
import re

from azure.keyvault.secrets import SecretClient
from urllib.parse import urlparse


class KeyVaultHook:

    def get_private_key(self, cert_url, credentials):
        url_parts = urlparse(cert_url)
        vault_url = "https://{}".format(url_parts.netloc)

        match = re.match(r'^\/certificates\/(.+)\/([a-f0-9]+)', url_parts.path, re.I)
        cert_name = match.group(1)
        cert_version = match.group(2)

        secret_client = SecretClient(vault_url=vault_url, credential=credentials)
        secret = secret_client.get_secret(name=cert_name, version=cert_version)

        return base64.b64decode(secret.value)
