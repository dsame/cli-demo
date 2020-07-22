import requests

from oml.util import auth
from oml.util.requests import handle_response


class GraphHook:

    def __init__(self):
        endpoint = 'https://graph.microsoft.com'
        token = auth.get_token(endpoint)
        self._session = requests.Session()
        self._session.headers.update({'Authorization': 'Bearer {}'.format(token['accessToken'])})
        self.users_endpoint = '/'.join([endpoint, 'beta', 'users'])

    @handle_response
    def get_user_by_email(self, email, params):
        params.update({'$filter': "mail eq '{}' or userPrincipalName eq '{}'".format(email, email), '$top': '1'})
        return self._session.get(self.users_endpoint, params=params)

    def get_user_domain_alias(self, email):
        params = {'$select': 'onPremisesDomainName,onPremisesSamAccountName'}
        user_data = self.get_user_by_email(email, params)['value'][0]
        alias = user_data['onPremisesSamAccountName']
        domain = user_data['onPremisesDomainName'].split('.')[0]
        return '{}\\{}'.format(domain.upper(), alias)
