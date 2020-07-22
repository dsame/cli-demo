import os
from adal import AuthenticationContext, TokenCache, AdalError

from oml.settings import (
    get_user_metadata,
    update_user_metadata,
    ADAL_TOKEN_FILE_PATH,
    AUTHORITY_URI,
    CLIENT_ID)


def get_token(resource):
    cache = _get_token_cache()
    context = AuthenticationContext(AUTHORITY_URI, cache=cache)

    token = None
    key = os.environ.get('OML_CLI_KEY')
    if key is not None:
        token = context.acquire_token_with_client_credentials(resource, CLIENT_ID, key)
    else:
        metadata = get_user_metadata()
        user = metadata.get('userId')
        if user is not None:
            try:
                token = context.acquire_token(resource, user, CLIENT_ID)
            except AdalError as e:
                # Password change error, prompt new login
                if('AADSTS50173' in e.error_response):
                    token = _get_new_token(context, cache, resource)

        if token is None:
            token = _get_new_token(context, cache, resource)

    return token


def _get_new_token(context, cache, resource):
    user_code = context.acquire_user_code(resource, CLIENT_ID)
    print(user_code['message'])
    token = context.acquire_token_with_device_code(resource, user_code, CLIENT_ID)
    _serialize_tokens(cache)
    update_user_metadata('userId', token['userId'])
    return token


def _serialize_tokens(cache: TokenCache):
    with open(ADAL_TOKEN_FILE_PATH, mode='w') as token_file:
        token_file.write(cache.serialize())


def _get_token_cache() -> TokenCache:
    if not os.path.exists(ADAL_TOKEN_FILE_PATH):
        return TokenCache()

    with open(ADAL_TOKEN_FILE_PATH) as token_file:
        return TokenCache(token_file.read())
