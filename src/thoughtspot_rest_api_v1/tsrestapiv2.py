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
    #
    # /metadata/ endpoints
    #
    #

    #
    # /metadata/tag endpoints
    #
    def metadata_tag(self, tag_name: Optional[str] = None, tag_guid: Optional[str] = None):
        endpoint = 'metadata/tag'

        url = self.base_url + endpoint
        if tag_guid is not None:
            url_params = {
                'id': tag_guid
            }
        elif tag_name is not None:
            url_params = {
                'name': tag_name
            }
        else:
            raise SyntaxError('Must specify either tag_guid or tag_name argument')

        response = self.requests_session.get(url=url, params=url_params)

        response.raise_for_status()
        return response.json()

    def metadata_tag_create(self, tag_name: str, color_hex_code: Optional[str] = None):
        endpoint = 'metadata/tag/create'

        url = self.base_url + endpoint

        json_post_data = {'name': tag_name}
        if color_hex_code is not None:
            json_post_data['color'] = color_hex_code

        response = self.requests_session.post(url=url, json=json_post_data)

        response.raise_for_status()
        return response.json()

    def metadata_tag_update(self, tag_guid: str, tag_name: Optional[str] = None, color_hex_code: Optional[str] = None):
        endpoint = 'metadata/tag/update'

        url = self.base_url + endpoint

        if tag_name is None and color_hex_code is None:
            raise SyntaxError('One of tag_name or color_hex_code must have a value')

        json_post_data = {'id': tag_guid}

        if tag_name is not None:
            json_post_data['name'] = tag_name
        if color_hex_code is not None:
            json_post_data['color'] = color_hex_code

        response = self.requests_session.put(url=url, json=json_post_data)

        response.raise_for_status()
        return True

    def metadata_tag_delete(self, tag_guid: Optional[str] = None, tag_name: Optional[str] = None):
        endpoint = 'metadata/tag/delete'

        url = self.base_url + endpoint

        if tag_guid is not None:
            url_params = {
                'id': tag_guid
            }
        elif tag_name is not None:
            url_params = {
                'name': tag_name
            }
        else:
            raise SyntaxError('Must specify either tag_guid or tag_name argument')

        response = self.requests_session.delete(url=url, params=url_params)

        response.raise_for_status()
        return True

    # Documentation calls for a List of Dicts with their types for tsObject
    # We provide a simple List of GUIDs and specifying one type as more common use case,
    # with ts_object_mixed_types available for the full structure
    def metadata_tag_assign(self, tag_guid: Optional[str] = None, tag_name: Optional[str] = None,
                            object_guid_list: Optional[List[str]] = None, object_type: Optional[str] = None,
                            ts_object_mixed_types: Optional[List[Dict]] = None
                            ):
        endpoint = 'metadata/tag/assign'

        url = self.base_url + endpoint

        if tag_guid is not None:
            json_post_data = {
                'id': tag_guid
            }
        elif tag_name is not None:
            json_post_data = {
                'name': tag_name
            }
        else:
            raise SyntaxError('Must specify either tag_guid or tag_name argument')

        # If user passes in the data structure
        if ts_object_mixed_types is not None:
            json_post_data['tsObject'] = ts_object_mixed_types
        else:
            if object_guid_list is None and object_type is None:
                raise SyntaxError('Must pass both object_guid_list or object_type together or ts_object_mixed_types')
            objects_list = []
            for guid in object_guid_list:
                objects_list.append({'id' : guid, 'type': object_type})
            json_post_data['tsObject'] = objects_list

        response = self.requests_session.put(url=url, json=json_post_data)

        response.raise_for_status()
        return True

    # Documentation calls for a List of Dicts with their types for tsObject
    # We provide a simple List of GUIDs and specifying one type as more common use case,
    # with ts_object_mixed_types available for the full structure
    def metadata_tag_unassign(self, tag_guid: Optional[str] = None, tag_name: Optional[str] = None,
                              object_guid_list: Optional[List[str]] = None, object_type: Optional[str] = None,
                              ts_object_mixed_types: Optional[List[Dict]] = None
                              ):
        endpoint = 'metadata/tag/unassign'

        url = self.base_url + endpoint

        if tag_guid is not None:
            json_post_data = {
                'id': tag_guid
            }
        elif tag_name is not None:
            json_post_data = {
                'name': tag_name
            }
        else:
            raise SyntaxError('Must specify either tag_guid or tag_name argument')

        # If user passes in the data structure
        if ts_object_mixed_types is not None:
            json_post_data['tsObject'] = ts_object_mixed_types
        else:
            if object_guid_list is None and object_type is None:
                raise SyntaxError('Must pass both object_guid_list or object_type together or ts_object_mixed_types')
            objects_list = []
            for guid in object_guid_list:
                objects_list.append({'id' : guid, 'type': object_type})
            json_post_data['tsObject'] = objects_list

        response = self.requests_session.put(url=url, json=json_post_data)

        response.raise_for_status()
        return True

    def metadata_delete(self, object_type: str, guids: List[str], ):
        endpoint = 'metadata/delete'

        url = self.base_url + endpoint

        # Current spec calls for a GET with a -d argument in cURL, but this translates to a URL param not body
        url_params = {
            'type': object_type,
            'id': guids
        }

        response = self.requests_session.delete(url=url, params=url_params)

        response.raise_for_status()
        return True
    #
    # /connection/ endpoints
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

        # Current spec calls for a GET with a -d argument in cURL, but this translates to a URL param not body
        url_params = {
            'id': guid
        }

        response = self.requests_session.get(url=url, params=url_params)

        response.raise_for_status()
        return response.json()

    # Needs testing because the url param format is to have repeated use of 'vizId'
    def data_liveboard_query_sql(self, guid: str, viz_ids: Optional[List[str]] = None):
        endpoint = 'data/liveboard/querysql'

        url = self.base_url + endpoint
        url_params = {
            'id': guid
        }
        if viz_ids is not None:
            url_params['vizId'] = viz_ids
        response = self.requests_session.get(url=url, params=url_params)

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

        response = self.requests_session.post(url=url, json=json_post_data,
                                              headers={'Accept': 'application/octet-stream'})
        response.raise_for_status()
        return response.content

    def report_liveboard(self, guid: str,
                         report_type: str = 'PDF',
                         viz_ids: Optional[List[str]] = None,
                         landscape_or_portrait: str = 'LANDSCAPE',
                         cover_page: bool = True,
                         logo: bool = True,
                         page_numbers: bool = False,
                         filter_page: bool = True,
                         truncate_tables: bool = False,
                         footer_text: str = None,
                         ):
        # one_visualization_per_page: bool = False,  -- appears to be missing from V2 API vs. V1
        endpoint = 'report/liveboard'

        url = self.base_url + endpoint

        json_post_data = {'id': guid,
                          'type': report_type,
                          'vizId': viz_ids
                          }
        if report_type == 'PDF':
            json_post_data['pdfOptions'] = {
                'orientation': landscape_or_portrait,
                'truncateTables': truncate_tables,
                'includeLogo': logo,
                'footerText': footer_text,
                'includePageNumber': page_numbers,
                'includeCoverPage': cover_page,
                'includeFilterPage': filter_page
            }

        response = self.requests_session.post(url=url, json=json_post_data,
                                              headers={'Accept': 'application/octet-stream'})
        response.raise_for_status()
        return response.content

    #
    # /security/ endpoints
    #

    def security_permission_tsobject(self, guid: str, object_type: str, include_dependents: bool = False):
        endpoint = 'security/permission/tsobject'

        url = self.base_url + endpoint

        url_params = {
            'id': guid,
            'type': object_type,
            'includeDependent': include_dependents
        }

        response = self.requests_session.get(url=url, params=url_params)

        response.raise_for_status()
        return response.json()

    def security_permission_principal(self,
                                      user_or_group_guid: Optional[str] = None,
                                      username_or_group_name: Optional[str] = None):
        endpoint = 'security/permission/principal'

        url = self.base_url + endpoint
        if user_or_group_guid is not None:
            url_params = {
                'id': user_or_group_guid
            }
        elif username_or_group_name is not None:
            url_params = {
                'name': username_or_group_name
            }
        else:
            raise SyntaxError('Must specify either user_or_group_guid or username_or_group_name argument')

        response = self.requests_session.get(url=url, params=url_params)

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


'''
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
'''