import os
import requests.exceptions

# from thoughtspot_rest_api_v1 import *
from src.thoughtspot_rest_api_v1 import *

# Details about objects within ThoughtSpot all are accessed through 'metadata/' endpoints, which can be used
# for almost every object type


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


#
# Users and Groups
#

# in the V2 API, the /search endpoints have very flexible request formats, that allow for very detailed searches
# Passing in an empty request {} will get a full listing

# Users Listing
print("\nAll Users Listing from users/search")
# Empty request gets all details
users = ts.users_search(request={})
print(users)

# Search for specific user
search_request = {
    'user_identifier': '{nameOrGuid}'
}
users = ts.users_search(request=search_request)
print(users)

# Users who belong to given group
search_request = {
    'group_identifiers': ['{groupNameOrGuid}']
}
users = ts.users_search(request=search_request)
print(users)


# Group Listing
print("\nGroups Listing")
groups = ts.groups_search(request={})
print(groups)

print("\nGroups Listing for a particular user")
search_request = {
    'user_identifiers': ['{nameOrGuid}']
}
groups = ts.groups_search(request=search_request)
print(groups)

# Each group object returned will hav a 'users' property, which includes both username and GUID for each user
# Lots of other good stuff in the response from groups/search
for group in groups:
    print("Group {} called {}".format(group['name'], group['display_name']))
    print(group['users'])


#
# Data objects
#

# metadata/search has very large number of options for the request. Please see the Playground for all the possibilities

# Get all Tables
search_request = {
    'metadata': {'type': 'LIVEBOARD'},
    'record_offset': 0,
    'record_size': 10000  # default is 10
}
tables = ts.metadata_search(request=search_request)

print(tables)

# Tables created by a user
search_request = {
    'metadata': {'type': 'LIVEBOARD'},
    'created_by_user_identifiers': ['bryant.howell'],
    'record_offset': 0,
    'record_size': 10000  # default is 10
}
tables = ts.metadata_search(request=search_request)
print(tables)
# You can use this pattern for all the various metadata object requests
