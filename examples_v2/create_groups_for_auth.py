import os
import requests.exceptions
import json

from thoughtspot_rest_api_v1 import *

#
# Script showing creating Groups on the fly for auth purposes and assigning
# various entitlements
#
#

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

org_id = 0  # Set to org_id in multi-tenant environment

ts: TSRestApiV2 = TSRestApiV2(server_url=server)

# Column sharing requires V1 REST API prior to 10.5
ts1: TSRestApiV1 = TSRestApiV1(server_url=server)

try:
    auth_token_response = ts.auth_token_full(username=username, password=password, validity_time_in_sec=3000)
    ts.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

# Roles are collections of privileges that can be assigned to Groups
# You can use existing roles, using their name or GUID:
try:
    roles_req = {
        "role_identifiers": ["{Role Name}"]
    }
    roles_list = ts.roles_search(request=roles_req)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

# or you can create a new role and assign it to the new group
try:
    roles_create_req = {
      "name": "Role For User X",
      "privileges": [
        "GROUP_ADMINISTRATION",
        "DATADOWNLOADING",
        "DEVELOPER"
      ]
    }
    new_role = ts.roles_create(request=roles_create_req)
    new_role_guid = new_role['id']

except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

# Create a group with the new role from above
new_group_name = "{name_use_for_rls_rules}"
new_group_display_name = new_group_name  # or make a nicer name
group_create_req = {
    "name": new_group_name,
    "display_name": new_group_display_name,
    "type": "LOCAL_GROUP",
    "visibility": "NON_SHARABLE",
    "role_identifiers": [new_role_guid]
}

try:
    new_group = ts.groups_create(request=group_create_req)
    new_group_guid = new_group['id']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

# Access control is set via Sharing

# Example request to pull all LOGICAL_TABLES (Tables and Worksheets) with a particular tag
md_search_req = {
    "record_offset": 0,
    "record_size": -1,
    "metadata": [
        {
            "type": "LOGICAL_TABLE"
        }
    ],
    "tag_identifiers": [
        "Standard Tables"
    ]
}

try:
    all_log_tables = ts.metadata_search(request=md_search_req)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

# This shows V2.0 API which you can use for anything other than COLUMNS, at the moment

metadata_ids = []
# Process through the results list and do any additional logic to get final set of IDs
for log_table in all_log_tables:
    metadata_ids.append(log_table['metadata_id'])

share_request = {
  "permissions": [
    {
      "principal": {
        "identifier": new_group_guid
      },
      "share_mode": "READ_ONLY"
    }
  ],
  "emails": [],
  "message": "no message",
  "enable_custom_url": False,
  "notify_on_share": False,
  "has_lenient_discoverability": False,
  "metadata_identifiers": metadata_ids,
  "metadata_type": "LOGICAL_TABLE"
}

try:
    ts.security_metadata_share(request=share_request)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

##
## V1 API for LOGICAL_COLUMNS
##

# The LOGICAL_COLUMN objects of a given Table or Worksheet are available under
# metadata_detail.columns of the response if you choose include_details: true
log_cols_search_req = {
    "record_offset": 0,
    "record_size": -1,
    "metadata": [
        {
            "type": "LOGICAL_TABLE",
            "identifier": "{guid_of_table_or_worksheet}"
        }
    ],
    "include_details": True
}

try:
    tables_resp = ts.metadata_search(request=log_cols_search_req)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

col_ids_to_share =[]
if len(tables_resp) == 1:
    cols = tables_resp[0]['metadata_details']['columns']
    for col in cols:
        col_name = col["header"]["name"]
        col_id = col["header"]["id"]
        # any additional logic here to determine which IDs to send to sharing request

        col_ids_to_share.append(col_id)



# Finally - you can assign the new Group to a user either via Update User
# or the Full Access Token request using the JIT provisioning feature