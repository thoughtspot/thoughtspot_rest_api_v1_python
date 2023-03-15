import os
import requests.exceptions

from thoughtspot_rest_api_v1 import *

# You are probably better off looking at https://github.com/thoughtspot/cs_tools for more complete versions of this
# functionality, but this shows how to use the REST APIs directly to put together various information in ways
# that aren't available directly in the ThoughtSpot UI

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

read_only_guids = ['{group1Guid}', '{group2Guid}']
edit_guids = ['{guid4Guid']
lb_guid = 'lbGuid'


ts = TSRestApiV2(server_url='https://a.thoughtspot.cloud')
try:
    auth_token_response = ts.auth_token_full(username=username, password=password, validity_time_in_sec=3000)
    ts.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

# V2 allows for complex queries to see the permissions
principals_request = {
    'principals': [{'type': 'USER', 'identifier': '{usernameOrGuid}'}]
}

# principals_request = {
#    'principals': [{'type': 'USER_GROUP', 'identifier': '{groupnameOrGuid}'}]
# }

principal_perms = ts.security_principals_fetch_permissions(request=principals_request)

metadata_request = {
    'metadata': [{'type': 'LIVEBOARD', 'identifier': '{lbNameOrGuid}'}],
    'include_dependent_objects': False
}
object_perms = ts.security_metadata_fetch_permissions(request=metadata_request)

# Share objects
# To actually set sharing for an object

# You build out who and what permissions to give on the content in the permissions: [ {PRINCIPALS}] array
sharing_request = {
    'metadata_type': "LIVEBOARD",
    'metadata_identifiers': ['{lbGuid1}', '{lbGuid2}'],
    'permissions': [
        {'principal':
            {
                'identifier': "{groupNameorGuid}",
                'type': 'USER_GROUP'
            },
         'share_mode': 'READ_ONLY'
       }
    ]
}
ts.security_metadata_share(request=sharing_request)