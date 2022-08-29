from collections import OrderedDict
from typing import Optional, Dict, List, Union
import json

import requests

#
# Very simple implementation of V2 REST API
# There will eventually be a standard Python SDK
# Only intended for features in V2 that are not in V1, while the V2 API is being finalized
#


class TSRestApiV2:
    """
    The TSRestApiV2 implementation is a simple implementation to provide access to methods that
    do not exist in V1 at this time, as well as providing a requests.Session object to issue any other
    V2 call the user desires. It is meant as a bridge until the official V2 SDKs are available, and a companion
    to the existing TSRestApiV1 library here
    """
    def __init__(self, server_url: str):
        # Protect from extra end slash on URL
        if server_url[-1] == '/':
            server_url = server_url[0:-1]

        self.server = server_url

        # REST API uses cookies to maintain the session, so you need to create an open Session
        self.requests_session = requests.Session()

        # X-Requested-By             is necessary for all calls.
        # Accept: application/json   isn't necessary with requests (default: Accept: */*) but might be in other frameworks
        #
        # This sets the header on any subsequent call
        self.api_headers = {'X-Requested-By': 'ThoughtSpot', 'Accept': 'application/json', 'Accept-Language': 'en_US'}
        self.requests_session.headers.update(self.api_headers)

        # TS documentation shows the /tspublic/v2/ portion but it is always preceded by {server}/callosum/v2/
        self.base_url = '{server}/tspublic/rest/v2/'.format(server=self.server)
        self.non_public_base_url = '{server}/callosum/v1/'.format(server=self.server)

    #
    # Session management calls
    # - up here vs. in the SESSION section below (because these two are required)
    #
    def session_login(self,  username: Optional[str] = None, password: Optional[str] = None,
                      token: Optional[str] = None) -> requests.Session:
        endpoint = 'session/login'

        url = self.base_url + endpoint

        if token is not None:
            response = self.requests_session.post(url=url, headers={"Authorization": "Bearer {}".format(token)})
        elif username is not None and password is not None:
            json_post_data = {'userName': username, 'password': password, 'rememberMe': 'true'}
            response = self.requests_session.post(url=url, json=json_post_data)
        else:
            raise Exception("If using username/password, must include both")

        # HTTP 204 - success, no content
        response.raise_for_status()
        return self.requests_session

    def session_logout(self) -> bool:
        endpoint = 'session/logout'

        url = self.base_url + endpoint
        response = self.requests_session.post(url=url)

        # HTTP 204 - success, no content
        response.raise_for_status()
        return True

    # This is only the V2 API bearer token, not the Trusted Authentication token from V1
    def get_token(self, username: Optional[str] = None, password: Optional[str] = None,
                  secret_key: Optional[str] = None, token_expiry_duration: int = 300,
                  access_level: str = "FULL", ts_object_id: Optional[str] = None) -> Dict:
        endpoint = 'session/gettoken'

        url = self.base_url + endpoint

        json_post_data = {'accessLevel': access_level,
                          'tokenExpiryDuration': token_expiry_duration}

        if secret_key is not None:
            json_post_data['secretKey'] = secret_key
        elif username is not None and password is not None:
            json_post_data['userName'] = username
            json_post_data['password'] = password
        else:
            raise Exception("If using username/password, must include both")

        if ts_object_id is not None:
            json_post_data['tsObjectId'] = ts_object_id

        response = self.requests_session.post(url=url, json=json_post_data)

        response.raise_for_status()
        return response.json()

    def session_revoke_token(self) -> bool:
        endpoint = 'session/revoketoken'

        url = self.base_url + endpoint
        response = self.requests_session.post(url=url)

        # HTTP 204 - success, no content
        response.raise_for_status()
        return True

    #
    # Generic wrappers for the basic HTTP methods
    #

    #
    # /data/ endpoints
    #

    def data_answer_data(self, guid: str, offset: int = None, batch_number: int = None,
                         batch_size: int = None, format_type: str = None):
        endpoint = 'session/gettoken'

        url = self.base_url + endpoint

        json_post_data = {'id': guid }

        if offset is not None:
            json_post_data['offset'] = offset
        if batch_number is not None:
            json_post_data['batchNumber'] = batch_number
        if batch_size is not None:
            json_post_data['batchSize'] = batch_size
        if format_type is not None:
            json_post_data['formatType'] = format_type

        response = self.requests_session.post(url=url, json=json_post_data)

        response.raise_for_status()
        return response.json()