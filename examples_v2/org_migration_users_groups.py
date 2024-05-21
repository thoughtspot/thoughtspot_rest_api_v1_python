import os
import requests.exceptions

from src.thoughtspot_rest_api_v1 import *

#
# Example order of actions to "move" users and groups from primary (org_id=0) to
# a new org just for that set of users
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


# if given a list of usernames, will add to dest_org using users/update on primary org
def add_users_to_dest_org(users_list: List[str] = []):
    for user in users_list:
        user_update_req = {
            "operation": "ADD",
            "org_identifiers": [str(dest_org_id)]
        }

        print("Updating user {} to add to Org {}".format(user, dest_org_id))
        update_resp = dest_org.users_update(user_identifier=user, request=user_update_req)

def remove_users_from_orig_org(users_list: List[str] = []):
    for user in users_list:
        user_update_req = {
            "operation": "REMOVE",
            "org_identifiers": [str(dest_org_id)]
        }

        print("Removing user {} to add to Org {}".format(user, 0))
        update_resp = dest_org.users_update(user_identifier=user, request=user_update_req)


# You may want to get users that are currently in a group and put all of them
# On another org
def get_user_list_from_group(group_name) -> List[str]:
    group_search_req = {
        "record_offset": 0,
        "record_size": -1,
        "group_identifier": group_name,
        "org_identifiers": ["0"]  # if getting from primary
    }
    groups_resp = org0.groups_search(request=group_search_req)
    users = []
    if len(groups_resp) == 1:
        for user in groups_resp[0]["users"]:
            users.append(user["id"])
            # You COULD use the username like below
            # users.append(user["name"])
    return users


def create_groups_on_dest_org(groups_list, users_list: Optional[List] = None, visibility="NON_SHARABLE"):
    for group in groups_list:

        new_group_req = {
                "name": group["name"],
                "display_name": group['display_name'],
                "type": "LOCAL_GROUP",
                "visibility": visibility
        }
        if users_list is not None:
            # Some groups you may want to be SHARABLE
            new_group_req["user_identifiers"] = users_list  # This would put ALL users into these groups - may not want
        new_group_resp = dest_org.groups_create(request=new_group_req)

# Actual steps, feel free to comment out however you feel, or implement command-line arguments
def main():
    # Moving users from a specific group
    group_name_to_move_to_dest_org = "Customer A Group"
    # All the users
    users_in_group = get_user_list_from_group(group_name=group_name_to_move_to_dest_org)

    # Add the users to the destination org
    add_users_to_dest_org(users_list=users_in_group)

    # Do you need any new groups in the destination org?
    # Simple pattern to create with name / display name,
    new_groups_to_create = [
        {"name": "new_group_1", "display_name": "New Group 1"}
    ]
    create_groups_on_dest_org(new_groups_to_create, users_list=users_in_group)



if __name__ == "__main__":
    main()
