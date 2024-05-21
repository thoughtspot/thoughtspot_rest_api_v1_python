import os
import requests.exceptions

from src.thoughtspot_rest_api_v1 import *

#
# Example order of actions to "move" data and content objects
# from primary org to a destination org
# Then share to groups on the destination org (see org_migration_users_groups.py for user/group migration)
#

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

dest_org_name = 'Customer A'
# Create two org objects, one for org0 and one of the destination org, to insure separation
# in the actions
#
# If you are doing transfer from non-primary org (org 0) to another, you may use the below to retrieve BOTH
# org IDs from org0, then create an orig_org object along with dest_org below
#

org0: TSRestApiV2 = TSRestApiV2(server_url=server)
try:
    auth_token_response = org0.auth_token_full(username=username, password=password,
                                               validity_time_in_sec=3000, org_id=0)
    org0.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

# Get the org_id for the destination org (must be an admin level account)
org_search_req = {
    "org_identifier": dest_org_name
}
org_search_resp = org0.orgs_search(request=org_search_req)
if len(org_search_resp) == 1:
    dest_org_id = org_search_resp[0]['id']
else:
    # This just exits, but you could instead create the Org
    print("Could not find Org named {}, exiting...".format(dest_org_name))
    exit()

    # Example code to create Org with destination name:

    # new_org_resp = org0.orgs_create(name=dest_org_name)
    # dest_org_id = new_org_resp["id"]


# Create dest_org object using the org_id retrieved from request to primary org
dest_org = TSRestApiV2 = TSRestApiV2(server_url=server)
try:
    auth_token_response = dest_org.auth_token_full(username=username, password=password, validity_time_in_sec=3000,
                                                   org_id=dest_org_id)
    dest_org.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()


def create_new_connection_from_primary(connection_to_replicate, new_connection_name, new_connection_password):

    # Create connection on destination org (need to get credentials from secure storage)
    orig_conn_config = connection_to_replicate["details"]["configuration"]
    orig_conn_config["password"] = new_connection_password
    # Must replace the password, it w
    conn_create_req = {
          "name": new_connection_name,
          "data_warehouse_type": connection_to_replicate["data_warehouse_type"],
          "data_warehouse_config": orig_conn_config,
          "validate": False
    }
    try:
        new_conn_resp = dest_org.connection_create(request=conn_create_req)
        return new_conn_resp["id"]
    except requests.exceptions.HTTPError as e:
        print(e)
        print(e.response.content)
        exit()


# Actual steps, feel free to comment out however you feel, or implement command-line arguments
def main():
    connection_name_to_replicate = "Customer A Connection"
    new_connection_name = "Main Connection"  # change if you need to, you can have same name across Orgs if you like
    # Fill in more details if you need more specific
    # "include_details: True lets us get the connection_config to use in the creation step
    connection_id_req = {
        "record_offset": 0,
        "record_size": 10,
        "authentication_type": "SERVICE_ACCOUNT",
        "include_details": True,
        "connections": [
            {
                "identifier": connection_name_to_replicate
            }
        ]
    }
    conn_search_resp = org0.connection_search()
    if len(conn_search_resp) == 1:
        conn_to_replicate = conn_search_resp[0]

    else:
        print("Connection name {} returns more than one connection, specify ID".format(connection_name_to_replicate))
        exit()

    connection_id_to_replicate = conn_search_resp[0]["id"]
    # Or alternatively, create the connection in the UI
    new_conn_id = create_new_connection_from_primary(connection_to_replicate=conn_to_replicate,
                                                     new_connection_name=new_connection_name,
                                                     new_connection_password="{getCredentialsSomehow}")

    # new_conn_id = "{guidCopiedFromUI}"

    # Get all data objects from the primary org on particular connection
    # Tables come from /connection/search -> ["details"]["tables"]
    tables_on_orig_conn = conn_to_replicate["details"]["tables"]

    # From the tables, you can use /metadata/search to retrieve all dependents,
    # or use /metadata/tml/export with "export_associated": true

    # For the sake of reducing duplication, make first calls to get the total set of TML to export / reimport

    # If Connection Name is different between the two orgs, you'll need to adjust the TML objects
    # use https://github.com/thoughtspot/thoughtspot_tml library for each object access all properties

if __name__ == "__main__":
    main()
