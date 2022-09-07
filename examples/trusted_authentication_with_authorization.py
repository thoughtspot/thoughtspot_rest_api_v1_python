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
from dotenv import load_dotenv
load_dotenv()

# from thoughtspot_rest_api_v1 import *
from src.thoughtspot_rest_api_v1.tsrestapiv1 import *

#
# Simple JSON format for defining user details including groups. You will need to determine how to get these details
# in your own service (perhaps a JWT with similar properties, or existing application session details
#
user_details = {
    "username": 'new_user_1',
    "full_name": "New User 1",
    "email": "new.user.1@domain.net",
    'tenant_group': 'cust1001292',
    'privilege_groups': ['read_only', 'see_data'],
    'access_control_groups': ['standard_reports', 'manager_reports']
}

#
# Simple example of the full set of REST API commands one might use for user creation, group assignment, etc.
# in an authenticator service for trusted authentication
# Note: does not define secure storage of credentials, secret_key or the message from the browser / web application
#

#
#
#
thoughtspot_server = os.getenv('server')        # or type in yourself
service_acct_username = os.getenv('username')  # or type in yourself
service_acct_password = os.getenv('password')  # or type in yourself
secret_key = os.getenv('secret_key')  # or type in yourself

ts: TSRestApiV1 = TSRestApiV1(server_url=thoughtspot_server)


# Wrapped in function to call as part of a retry loop when used in a long-running server / service process
def login():
    try:
        ts.session_login(username=service_acct_username, password=service_acct_password)
    except requests.exceptions.HTTPError as e:
        print(e)
        print(e.response.content)


login()


def get_username(request):
    #
    # This might involve parsing a JWT from your IdP or retrieving the username based on session cookie, etc.
    # Example here is just reading 'username' property from the simple JSON-style object
    #
    return request['username']


def get_user_full_name(request):
    #
    # This might involve parsing a JWT from your IdP or retrieving the other details based on session cookie, etc.
    # Example here is just reading 'full_name' property from the simple JSON-style object
    #
    return request['full_name']


def get_user_email(request):
    #
    # This might involve parsing a JWT from your IdP or retrieving the other details based on session cookie, etc.
    # Example here is just reading 'full_name' property from the simple JSON-style object
    #
    return request['email']


def get_user_groups(request):
    #
    # This might involve parsing a JWT from your IdP or retrieving the other details based on session cookie, etc.
    # Example here is just reading 'full_name' property from the simple JSON-style object
    #
    return request['users']


def create_user(rest_api_obj: TSRestApiV1, username, display_name, email, groups_guid):

    # REST API requires setting a password for users, but it is never used with SSO
    # Randomly generate password and set it when creating using
    letters = string.ascii_letters
    user_password = ''.join(random.choice(letters) for i in range(20))

    new_user_guid = rest_api_obj.user_post(username=username, password=user_password, display_name=display_name,
                                           groups=groups_guid)
    if email is not None:
        rest_api_obj.user_email(user_guid=new_user_guid, user_email=email)

    return new_user_guid


# Example of overall routine to process an inbound message
def web_request(request):

    # Verify the user_details request as valid, well-formed, from the right place, etc.
    # Not actually defined in this example, since it will vary on your own application / environment
    # response = validate_request_get_response(request)

    # For simplified example, we'll assume response was validated and equals the user_details JSON-style object above
    response = user_details
    user_username = get_username(response)

    # Step 1: See if username exists in ThoughtSpot, if not, create user
    try:
        users_in_ts = ts.user_get(name=user_username)
    # Attempt to re-login wtih the service account and send the REST API request again
    except requests.exceptions.HTTPError:
        # try to sign-in again
        login()
        try:
            users_in_ts = ts.user_get(name=user_username)
        except requests.exceptions.HTTPError:
            # print some type of error to log
            # Return an HTTP error response to the front-end, rather than login token
            return ErrorResponseToBrowser

    try:
        # Get the groups for use in the next step to add to users
        all_groups = ts.group_get()
    except requests.exceptions.HTTPError:
        # print some type of error to log
        # Return an HTTP error response to the front-end, rather than login token
        return ErrorResponseToBrowser

    # Parse out any group information for the user
    groups_for_user = get_user_groups(request)
    #
    # If user does not exist, create the user
    #
    if len(users_in_ts) == 0:
        user_full_name = get_user_full_name(response)
        user_email = get_user_email(response)

        user_guid = create_user(rest_api_obj=ts, username=user_username, display_name=user_full_name,
                                    email=user_email, groups_guid=[])
    else:
        user = users_in_ts[0]
        user_guid = user['id']

    # Step 2: Add user to groups, create groups if they don't exist (if that is your desired behavior)
    if groups_for_user > 0:
        # Get the GUIDs for the desired group names
        group_guid_list = []
        group_names_that_exist = []
        for group in all_groups:
            if group['name'] in groups_for_user:
                group_guid_list.append(group['id'])
                group_names_that_exist.append(group)

        # If you need to create arbitrary groups on the fly (for RLS)
        # go through and create, then add to the group_guid_list
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

        try:
            # POST only adds the user to the specified groups, vs. PUT which resets ALL of that user's groups
            # Depending on how you've configured, you might change to PUT to reset user to desired state
            ts.user_groups_post(user_guid=user_guid, group_guids=group_guid_list)
        except requests.exceptions.HTTPError:
            # print some type of error to log
            # Return an HTTP error response to the front-end, rather than login token
            return ErrorResponseToBrowser

    # Step 3: Request trusted token and return to the browser
    try:
        trusted_token = ts.session_auth_token(secret_key=secret_key, username=user_username, access_level='FULL')
    except requests.exceptions.HTTPError:
        # print some type of error to log
        # Return an HTTP error response to the front-end, rather than login token
        return ErrorResponseToBrowser

    # This will depend on the framework (WIP, will show in Flask eventually)
    return_token_to_browser(trusted_token)


