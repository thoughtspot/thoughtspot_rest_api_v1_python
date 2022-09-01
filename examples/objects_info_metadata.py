import os
import requests.exceptions

# from thoughtspot_rest_api_v1 import *
from src.thoughtspot_rest_api_v1.tsrestapiv1 import *

# Details about objects within ThoughtSpot all are accessed through 'metadata/' endpoints, which can be used
# for almost every object type


username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

ts: TSRestApiV1 = TSRestApiV1(server_url=server)
try:
    ts.session_login(username=username, password=password)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)

# Use the TSTypes enum for the object_type argument of the metadata_list or metadata_listobjectheaders calls

#
# Users and Groups
#

# User Listing
print("\nUsers Listing from metadata/list")
# metadata_list returns object with 'headers' key, which is the actual array of object headers
users = ts.metadata_list(object_type=TSTypes.USER)
print(users['headers'])

# metadata_listobjectheaders is the equivalent of the 'headers' key from metadata_list, so you can iterate the response
# directly
print("\nUsers Listing from metadata/listobjectheaders")
users = ts.metadata_listobjectheaders(object_type=TSTypes.USER)
print(users)

print("\nUsers Listing with Filter")
user = ts.metadata_list(object_type=TSTypes.USER, filter="bryant.howell")
print(user)
user_id = user['headers'][0]["id"]

# Group Listing
print("\nGroups Listing")
groups = ts.metadata_list(object_type=TSTypes.GROUP)
print(groups)
print("\nGroups Listing with Filter")
group = ts.metadata_list(object_type=TSTypes.GROUP, filter='Administrator')
print(group)
group_id = group['headers'][0]['id']

# Users in a Group
print("\nUsers in Group - ID {}".format(group_id))
users_in_group = ts.group_users_get(group_guid=group_id)
print(users_in_group)
for u in users_in_group:

    print(u.keys())
    print(u['header']['id'], u['header']['name'], u['header']['displayName'])

# What can a User or Group see (Sharing)
#objs_for_group = ts.group.list_available_objects_for_group(group_guid=group_id)
#print(objs_for_group)
#for obj in objs_for_group["headers"]:
#    print(obj)

#print("\n Available Objects for Users")
#objs_for_user = ts.user.list_available_objects_for_user(user_guid=user_id)
#print(objs_for_user)

#for obj in objs_for_user["headers"]:
#    print(obj)

# What Groups does a User Belong to (and other details)?
#print("\nPrivileges for User {}".format(user_id))
#user_privileges = ts.user.privileges_for_user(user_guid=user_id)
#print(user_privileges)

#print("\nAssigned Groups for User {}".format(user_id))
#user_assigned_groups = ts.user_groups__getuser_guid=user_id()
#print(user_assigned_groups)

#print("\nInherited Groups for User {}".format(user_id))
#user_inherited_groups = ts.user.inherited_groups_for_user(user_guid=user_id)
#print(user_inherited_groups)

#print("\nIs User {} a Super User".format(user_id))
#user_inherited_groups = ts.user.is_user_superuser(user_guid=user_id)
#print(user_inherited_groups)

#print("\nState of User {} ".format(user_id))
#user_inherited_groups = ts.user.state_of_user(user_guid=user_id)
#print(user_inherited_groups)

# Privileges for Group
#print("\nPrivileges for Group {}".format(group_id))
#group_privileges = ts.group.privileges_for_group(group_guid=group_id)
#print(group_privileges)

#
# Data objects
#

tables = ts.metadata_list(object_type=TSTypes.TABLE)
for obj in tables["headers"]:
    print(obj)
# The actual REST API has a 'type' and 'subtype' to specify the data objects, but the library
# will do the correct pattern when you use the TSTypes enum above. You could do this if you'd rather:
tables = ts.metadata_list(object_type=MetadataTypes.TABLE, subtypes=[MetadataSubtypes.TABLE])

worksheets = ts.metadata_list(object_type=TSTypes.WORKSHEET)

views = ts.metadata_list(object_type=TSTypes.VIEW)

sql_views = ts.metadata_list(object_type=TSTypes.SQL_VIEW)


#
# Content objects
#

answers = ts.metadata_list(object_type=TSTypes.ANSWER)

liveboards = ts.metadata_list(object_type=TSTypes.LIVEBOARD)
