import os
import requests.exceptions

from thoughtspot_rest_api_v1 import *

# This script uses the internal metadata/delete API endpoint, which will be unnecessary once the V2 API introduces
# a public form of delete. But it may be of use now

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

ts: TSRestApiV2 = TSRestApiV2(server_url=server)
try:
    auth_token_response = ts.auth_token_full(username=username, password=password, validity_time_in_sec=3000)
    ts.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

# You can use either GUID or name as 'identifier' property with V2 API. For 'metadata', you must add 'type' property
# when using a name as 'identifier', whereas with a GUID, 'type' is not required
tag_assign_request = {
    'tag_identifiers': ['Tag 1', 'Tag 3'],
    'metadata': [
        {'identifier': '{lbGUID1}'},
        {'identifier': '{lbGUID2}'}
    ]
}
ts.tags_assign(request=tag_assign_request)
