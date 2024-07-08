import os
import requests
import string
import random

#
# Framework of the most complete Trusted Authentication scenario, where a complex JWT is sent
# and REST API commands are used to provision user / assign to groups / create new RLS groups
# Intended to eventually be wrapped into a Flask process, but has not happened yet
# WIP
#

# I use a .env file locally to keep credentials out of the scripts themselves.
# You may want something more secure to protect admin credentials
# from dotenv import load_dotenv
# load_dotenv()

from thoughtspot_rest_api_v1 import *
#from src.thoughtspot_rest_api_v1.tsrestapiv1 import *

thoughtspot_server = os.getenv('server')        # or type in yourself
service_acct_username = os.getenv('username')  # or type in yourself
service_acct_password = os.getenv('password')  # or type in yourself


ts: TSRestApiV1 = TSRestApiV1(server_url=thoughtspot_server)


# Wrapped in function to call as part of a retry loop when used in a long-running server / service process
def login():
    try:
        ts.session_login(username=service_acct_username, password=service_acct_password)
    except requests.exceptions.HTTPError as e:
        print(e)
        print(e.response.content)


def create_user(rest_api_obj: TSRestApiV1, username, display_name, email, groups_guid):

    # REST API requires setting a password for users, but it is never used with SSO
    # Randomly generate password and set it when creating using
    letters = string.ascii_letters
    user_password = ''.join(random.choice(letters) for i in range(20))

    new_user_guid = rest_api_obj.user_post(username=username, password=user_password, display_name=display_name,
                                           properties={"mail" : email}, groups=groups_guid)
    # if email is not None:
    #    rest_api_obj.user_email(user_guid=new_user_guid, user_email=email)

    return new_user_guid



login()
try:
    # Get the groups for use in the next step to add to users
    all_groups = ts.group_get()
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()
print(all_groups)

groups_for_user = ['Test Group 1', 'Test Group 2']
# If you need to create arbitrary groups on the fly (for RLS)
# go through and create, then add to the group_guid_list

# Get the GUIDs for the desired group names
group_guid_list = []
group_names_that_exist = []
for group in all_groups:
    #print(group)
    if group['header']['name'] in groups_for_user:
        group_guid_list.append(group['header']['id'])
        group_names_that_exist.append(group['header']['name'])
print(group_names_that_exist)
groups_to_create = []
for group in groups_for_user:
    if group not in group_names_that_exist:
        groups_to_create.append(group)

for group in groups_to_create:
    # This is presuming for auto-created groups that group_name and display_name are identical
    # If they are not, you need to do more complex lookup so that you have both values here
    new_group_guid = ts.group_post(group_name=group, display_name=group, privileges=[],
                                   visibility=GroupVisibility.NON_SHARABLE)
    group_guid_list.append(new_group_guid)

create_user(rest_api_obj=ts, username='test_user_1', display_name='Test User 1', email='testuser1@domain.com',
            groups_guid=group_guid_list)
