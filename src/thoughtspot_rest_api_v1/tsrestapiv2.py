from collections import OrderedDict
from typing import Optional, Dict, List, Union
import json

import requests


class ReportTypes:
    PDF = 'PDF'
    XLSX = 'XLSX'
    CSV = 'CSV'
    PNG = 'PNG'


class TSTypesV2:
    LIVEBOARD = 'LIVEBOARD'
    ANSWER = 'ANSWER'
    DATAOBJECT = 'DATAOBJECT'
    COLUMN = 'COLUMN'


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
        endpoint = 'data/answer'

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

    def data_answer_query_sql(self, guid: str):
        endpoint = 'data/answer/querysql'

        url = self.base_url + endpoint

        # Current spec calls for a GET with a -d argument in cURL, but the id= argument is not JSON, just plain
        response = self.requests_session.get(url=url, data="id=".format(guid))

        response.raise_for_status()
        return response.json()

    def data_liveboard_query_sql(self, guid: str, viz_ids: Optional[List[str]] = None):
        endpoint = 'data/liveboard/querysql'

        url = self.base_url + endpoint

        # Current spec calls for a GET with a -d argument in cURL, but the id= argument is not JSON, just plain
        response = self.requests_session.get(url=url, data="id=".format(guid))

        response.raise_for_status()
        return response.json()

    #
    # /report/ endpoints
    #

    def report_answer(self, guid: str, report_type: str = 'PDF'):
        endpoint = 'report/answer'

        url = self.base_url + endpoint

        json_post_data = {'id': guid,
                          'type': report_type
                          }

        response = self.requests_session.post(url=url, json=json_post_data)

        return response.raw

    def report_liveboard(self, guid: str,
                         report_type: str = 'PDF',
                         viz_ids: Optional[List[str]] = None,
                         one_visualization_per_page: bool = False,
                         landscape_or_portrait: str = 'LANDSCAPE',
                         cover_page: bool = True,
                         logo: bool = True,
                         page_numbers: bool = False,
                         filter_page: bool = True,
                         truncate_tables: bool = False,
                         footer_text: str = None,
                         ):
        endpoint = 'report/liveboard'

        url = self.base_url + endpoint

        json_post_data = {'id': guid,
                          'type': report_type,
                          'vizId': viz_ids
                          }
        if report_type == 'PDF':
            json_post_data['pdfOptions'] = {
                'orientation'
            }

        response = self.requests_session.post(url=url, json=json_post_data)

        return response.raw

    #
    # /security/ endpoints
    #

    def security_permission_tsobject(self, guid: str, object_type: str, include_dependents: bool = False):
        endpoint = 'security/permission/tsobject'

        url = self.base_url + endpoint

        json_post_data = {
            'id': guid,
            'type': object_type,
            'includeDependent': include_dependents
        }

        response = self.requests_session.post(url=url, json=json_post_data)

        response.raise_for_status()
        return response.json()

    def security_permission_principal(self,
                                      user_or_group_guid: Optional[str] = None,
                                      username_or_group_name: Optional[str] = None):
        endpoint = 'security/permission/principal'

        url = self.base_url + endpoint
        if user_or_group_guid is not None:
            json_post_data = {
                'id': user_or_group_guid
            }
        elif username_or_group_name is not None:
            json_post_data = {
                'name': username_or_group_name
            }
        else:
            raise SyntaxError('Must specify either user_or_group_guid or username_or_group_name argument')

        response = self.requests_session.post(url=url, json=json_post_data)

        response.raise_for_status()
        return response.json()

    def security_permission_tsobject_search(self, guid: str, object_type: str, include_dependents: bool = False):
        endpoint = 'security/permission/tsobject/search'

        url = self.base_url + endpoint

        json_post_data = {
            'id': guid,
            'type': object_type,
            'includeDependent': include_dependents
        }

        response = self.requests_session.post(url=url, json=json_post_data)

        response.raise_for_status()
        return response.json()

    def security_permission_principal_search(self,
                                      user_or_group_guid: Optional[str] = None,
                                      username_or_group_name: Optional[str] = None):
        endpoint = 'security/permission/principal/search'

        url = self.base_url + endpoint
        if user_or_group_guid is not None:
            json_post_data = {
                'id': user_or_group_guid
            }
        elif username_or_group_name is not None:
            json_post_data = {
                'name': username_or_group_name
            }
        else:
            raise SyntaxError('Must specify either user_or_group_guid or username_or_group_name argument')

        response = self.requests_session.post(url=url, json=json_post_data)

        response.raise_for_status()
        return response.json()

    #
    # /admin/ endpoints
    #

    def admin_changeauthor(self, guids: List[str], from_username: Optional[str] = None,
                           from_user_guid: Optional[str] = None, to_username: Optional[str] = None,
                           to_user_guid: Optional[str] = None):
        endpoint = 'admin/changeauthor'

        url = self.base_url + endpoint

        json_post_data = {
            'tsObjectId': guids,
        }
        if from_username is not None:
            json_post_data['fromUser'] = {'name': from_username}
        elif from_user_guid is not None:
            json_post_data['fromUser'] = {'id': from_user_guid}
        else:
            raise SyntaxError("Must include one of from_username or from_user_guid")

        if to_username is not None:
            json_post_data['toUser'] = {'name': to_username}
        elif to_user_guid is not None:
            json_post_data['toUser'] = {'id': to_user_guid}
        else:
            raise SyntaxError("Must include one of to_username or to_user_guid")

        response = self.requests_session.put(url=url, json=json_post_data)

        response.raise_for_status()
        return True

    def admin_assignauthor(self, guids: List[str], to_username: Optional[str] = None,
                           to_user_guid: Optional[str] = None):
        endpoint = 'admin/assignauthor'

        url = self.base_url + endpoint

        json_post_data = {
            'tsObjectId': guids,
        }

        if to_username is not None:
            json_post_data['name'] = to_username
        elif to_user_guid is not None:
            json_post_data['id'] = to_user_guid
        else:
            raise SyntaxError("Must include one of to_username or to_user_guid")

        response = self.requests_session.put(url=url, json=json_post_data)

        response.raise_for_status()
        return True

    def admin_forcelogout(self, usernames: Optional[List[str]] = None, user_guids: Optional[List[str]] = None):
        endpoint = 'admin/forcelogout'

        url = self.base_url + endpoint

        users_list = []
        if usernames is not None:
            for username in usernames:
                users_list.append({'name': username})
        elif user_guids is not None:
            for user_guid in user_guids:
                users_list.append({'id': user_guid})
        else:
            raise SyntaxError("Must include one of usernames or user_guids")

        json_post_data = {
            'user': users_list
        }

        response = self.requests_session.post(url=url, json=json_post_data)

        response.raise_for_status()
        return True
