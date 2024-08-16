import os
import requests.exceptions
import json

from thoughtspot_rest_api_v1 import *

#
# Example order of actions to "move" data and content objects
# from primary org to a destination org
# Then share to groups on the destination org (see org_migration_users_groups.py for user/group migration)
#

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

org_names_to_deploy_to = [
    "dev",
    "test",
    "pre-prod",
    "cust_a",
    "cust_b"
]

connection_config_per_org = {
    "dev": {
              "accountName": "dev_db",
              "user": "tsadmin",
              "password": "TestConn123",
              "role": "sysadmin",
              "warehouse": "MEDIUM_WH"
            },
    "test": {
              "accountName": "test_db",
              "user": "tsadmin",
              "password": "TestConn123",
              "role": "sysadmin",
              "warehouse": "MEDIUM_WH"
            }
}

# Must log into Primary / Org 0 to get the list of Orgs, to get their org_id properties
org0: TSRestApiV2 = TSRestApiV2(server_url=server)
try:
    auth_token_response = org0.auth_token_full(username=username, password=password,
                                               validity_time_in_sec=3000, org_id=0)
    org0.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

for org_name in org_names_to_deploy_to:
    org_search_req = {
        "org_identifier": org_name
    }
    search_resp = org0.orgs_search(request=org_search_req)
    if len(search_resp) == 1:
        org_id = search_resp[0]['id']

        # Create bearer token for the org matching the org name
        ts: TSRestApiV2 = TSRestApiV2(server_url=server)
        try:
            auth_resp = ts.auth_token_full(username=username, password=password,
                                           validity_time_in_sec=3000, org_id=org_id)
            ts.bearer_token = auth_resp['token']
        except requests.exceptions.HTTPError as e:
            print(e)
            print(e.response.content)
            exit()

        # Connection details may vary between the different environments, so you'll need
        # to define the values and particularly the credentials to use for the connection
        # on each Org. We assume the NAME of the connection will be the same across connections

        # See https://developers.thoughtspot.com/docs/connections-api for configuration portion of JSON,
        # which is the same between V1 and V2 of this API
        create_req = {
            "name": "My Connection",
            "data_warehouse_type": "SNOWFLAKE",
            "data_warehouse_config": {
                "configuration": connection_config_per_org[org_name],
                "externalDatabases": []
            },
            "validate": False  # Must set to FALSE to create without adding tables initially
        }
        conn_create_resp = ts.connection_create(request=create_req)
        print("Created Connection: ")
        print(json.dumps(conn_create_resp, indent=2))