import os
import requests.exceptions
from thoughtspot_rest_api_v1 import *

#
# This script is an example of a workflow useful in a Git-based SDLC process
# It transfers the ownership of objects in ThoughtSpot to a Service Account
# Transfer Ownership command requires knowing the existing owner, so this takes
# the GUID inputs, finds the owners, and constructs the minimum number of ownership transfer commands
#

# Account to transfer content to (can also use GUID in V2)
transfer_to_username = 'service.account'

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

#
# REST API V2 features a transfer without knowing the object owner
#
ts: TSRestApiV2 = TSRestApiV2(server_url=server)
try:
    auth_token_response = ts.auth_token_full(username=username, password=password, validity_time_in_sec=3000)
    ts.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()


# 'type' is required in 9.1 and earlier versions, may eventually be unnecessary when passing GUIDs vs. names
# You can use ts.metadata_search to get the type of objects if you don't have
metadata_to_transfer = [
    {'type': 'LIVEBOARD', 'identifier': '{guid_1}'},
    {'type': 'LIVEBOARD', 'identifier': '{guid_2}'}
]
# Due to complexity of request, you define it completely here to pass to the actual method
transfer_request = {
    'metadata': metadata_to_transfer,
    'user_identifier': transfer_to_username,
    # You don't need to specify the original owner but you can as extra protection
    # current_owner_identifier: original_owner_id
}
ts.security_metadata_assign(request=transfer_request)


