import os
import json
import requests.exceptions
import csv

from thoughtspot_rest_api_v1 import *

# You are probably better of looking at https://github.com/thoughtspot/cs_tools for more complete versions of this
# functionality, but this shows how to use the REST APIs directly to put together various information in ways
# that aren't available directly in the ThoughtSpot UI

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

ts: TSRestApiV1 = TSRestApiV1(server_url=server)
try:
    ts.session_login(username=username, password=password)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)


def create_id_name_dict(listobjectheaders_response):
    mapping_dict = {}
    for a in listobjectheaders_response:
        mapping_dict[a["id"]] = a["name"]
    return mapping_dict


def get_permissions_for_all_objects(object_type, listobjectheaders_response, permission_type='DEFINED',
                                    dependent_share=True):
    id_map = create_id_name_dict(listobjectheaders_response)
    # Because the GUIDs pass in the URL, there is a limit to how many can be requested at a time
    # Must batch through the full set, make whatever number of requests, then put the whole thing together
    batch_size = 20
    guids_list = list(id_map.keys())
    # Reverse the list so that pop can run from the end of the list, more efficient
    guids_list.reverse()
    # Pop out the first elements in the batch size
    guids_to_retrieve = []
    for i in range(batch_size):
        guids_to_retrieve.append(guids_list.pop())
    # Get the first permissions object, we'll add the elements from subsequent calls to it
    perms = ts.security_metadata_permissions(object_type=object_type, object_guids=guids_to_retrieve,
                                             dependent_share=dependent_share, permission_type=permission_type)
    # The pop() action is reducing the list size so that eventually it will be at 0
    while len(guids_list) > 0:
        guids_to_retrieve = []
        for i in range(batch_size):
            # pop() throws IndexError once List is empty
            try:
                guids_to_retrieve.append(guids_list.pop())
            # break the loop after the last item
            except IndexError:
                break
        # Request the next batch of permissions by GUID
        next_perms = ts.security_metadata_permissions(object_type=object_type, object_guids=guids_to_retrieve,
                                                      dependent_share=dependent_share, permission_type=permission_type)
        for p in next_perms:
            perms[p] = next_perms[p]

    return perms


def map_names_to_permissions(listobjectheaders_response, permissions, users_map, groups_map):
    obj_id_map = create_id_name_dict(listobjectheaders_response)

    final_perms = permissions.copy()

    for perm in final_perms:
        # print(obj_id_map[perm], ":", perm)
        # Add name property
        perms_obj = final_perms[perm]["permissions"]
        final_perms[perm]["name"] = obj_id_map[perm]
        for p in perms_obj:
            # GUIDs can be for USER or USER_GROUP, this figures out which and marks along with adding the name
            if p in users_map:
                # print("  User: ", users_map[p], p)
                # Add User name and type
                final_perms[perm]["permissions"][p]["name"] = users_map[p]
                final_perms[perm]["permissions"][p]["type"] = "USER"
            if p in groups_map:
                # print("  Group: ", groups_map[p], p)
                # Add Group name and type
                final_perms[perm]["permissions"][p]["name"] = groups_map[p]
                final_perms[perm]["permissions"][p]["type"] = "USER_GROUP"
        # print("")
    return final_perms


def objects_without_permissions(permissions_object):
    final_obj = permissions_object.copy()
    for perm in permissions_object:
        if len(permissions_object[perm]["permissions"]) > 0:
            del final_obj[perm]
    return final_obj


def objects_with_permissions(permissions_object):
    final_obj = permissions_object.copy()
    for perm in permissions_object:
        if len(permissions_object[perm]["permissions"]) == 0:
            del final_obj[perm]
    return final_obj


def convert_permissions_objects_to_table(permissions_object, include_header=True):
    # order of table: Obj GUID, Obj Name, READ_ONLY Group Names, READ_ONLY Group GUIDs, READ_ONLY User Name, READ_ONLY GUIDS,
    # MODIFY Group Name, M Group GUID, M User Name, M User GUIDs
    header_row = ["Object GUID", "Obj Name", "READ_ONLY Group Names", "READ_ONLY Group GUIDs", "READ_ONLY User Name",
                  "READ_ONLY GUIDS", "MODIFY Group Names", "MODIFY Group GUIDs", "Modify User Names",
                  "Modify User GUIDs"]
    final_table = []
    if include_header is True:
        final_table.append(header_row)
    for p in permissions_object:
        row = []
        row.append(p)
        row.append(permissions_object[p]["name"])
        ro_group_names = []
        ro_group_guids = []
        ro_user_names = []
        ro_user_guids = []
        m_group_names = []
        m_group_guids = []
        m_user_names = []
        m_user_guids = []
        for a in permissions_object[p]["permissions"]:
            if permissions_object[p]["permissions"][a]["type"] == "USER_GROUP":
                if permissions_object[p]["permissions"][a]["shareMode"] == 'READ_ONLY':
                    ro_group_guids.append(a)
                    ro_group_names.append(permissions_object[p]["permissions"][a]["name"])
                if permissions_object[p]["permissions"][a]["shareMode"] == 'MODIFY':
                    m_group_guids.append(a)
                    m_group_names.append(permissions_object[p]["permissions"][a]["name"])
            if permissions_object[p]["permissions"][a]["type"] == "USER":
                if permissions_object[p]["permissions"][a]["shareMode"] == 'READ_ONLY':
                    ro_user_guids.append(a)
                    ro_user_names.append(permissions_object[p]["permissions"][a]["name"])
                if permissions_object[p]["permissions"][a]["shareMode"] == 'MODIFY':
                    m_user_guids.append(a)
                    m_user_names.append(permissions_object[p]["permissions"][a]["name"])
        row.append(ro_group_names)
        row.append(ro_group_guids)
        row.append(ro_user_names)
        row.append(ro_user_guids)
        row.append(m_group_names)
        row.append(m_group_guids)
        row.append(m_user_names)
        row.append(m_user_guids)
        final_table.append(row)
    return final_table

# Return groups with their permissions mapped to them
def permissions_by_group_or_user(permissions_object, groups_or_users_map):
    # { 'id' : { "name", "read_only_guids", "read_only_names", "modify_guids", "modify_names" }
    permission_map = {}
    for perm in permissions_object:
        for p in permissions_object[perm]["permissions"]:
            if p in groups_or_users_map:
                if p not in permission_map:
                    permission_map[p] = {}
                    permission_map[p]["name"] = permissions_object[perm]["permissions"][p]["name"]
                    permission_map[p]["read_only_guids"] = []
                    permission_map[p]["read_only_names"] = []
                    permission_map[p]["modify_guids"] = []
                    permission_map[p]["modify_names"] = []
                if permissions_object[perm]["permissions"][p]["shareMode"] == 'READ_ONLY':
                    permission_map[p]["read_only_guids"].append(p)
                    permission_map[p]["read_only_names"].append(permissions_object[perm]["name"])
                if permissions_object[perm]["permissions"][p]["shareMode"] == 'MODIFY':
                    permission_map[p]["modify_guids"].append(p)
                    permission_map[p]["modify_names"].append(permissions_object[perm]["name"])
    return permission_map


# Get users
users = ts.metadata_listobjectheaders(object_type=TSTypes.USER)
user_id_name_map = create_id_name_dict(users)

# Get groups
groups = ts.metadata_listobjectheaders(object_type=TSTypes.GROUP)
group_id_name_map = create_id_name_dict(groups)
# Permissions on liveboards


answers = ts.metadata_listobjectheaders(object_type=TSTypes.ANSWER)
a_perms = get_permissions_for_all_objects(object_type=TSTypes.ANSWER, listobjectheaders_response=answers)
a_perms_with_names = map_names_to_permissions(listobjectheaders_response=answers, permissions=a_perms,
                                              users_map=user_id_name_map, groups_map=group_id_name_map)

# Permissions call requires GUIDs, so must get list of all of them first
liveboards = ts.metadata_listobjectheaders(object_type=TSTypes.LIVEBOARD)

a_with_perms = objects_with_permissions(a_perms_with_names)
print(json.dumps(a_with_perms, indent=2))

a_without_perms = objects_without_permissions(a_perms_with_names)
print(json.dumps(a_without_perms, indent=2))

l_perms = get_permissions_for_all_objects(object_type=TSTypes.LIVEBOARD, listobjectheaders_response=liveboards)
print(l_perms)
l_perms_with_names = map_names_to_permissions(listobjectheaders_response=liveboards, permissions=l_perms,
                                              users_map=user_id_name_map, groups_map=group_id_name_map)


l_with_perms = objects_with_permissions(l_perms_with_names)
print(json.dumps(l_with_perms, indent=2))

perms_table = convert_permissions_objects_to_table(l_perms)
print(perms_table)
for p in perms_table:
    print (p)

# https://docs.python.org/3/library/csv.html
with open('permissions.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in perms_table:
        final_row = []
        for col in row:
            # This reduces the lists into comma delimited strings, otherwise you get [ ] around it
            # as the default way that Python stringifies lists
            if isinstance(col, list):
                if len(col) > 0:
                    final_row.append(", ".join(col))
                else:
                    final_row.append(None)
            else:
                final_row.append(col)
        csvwriter.writerow(final_row)

group_perms = permissions_by_group_or_user(l_perms, group_id_name_map)
print(group_perms)
for group in group_perms:
    print(group)
    print(group_perms[group])

user_perms = permissions_by_group_or_user(l_perms, user_id_name_map)
print(user_perms)
for u in user_perms:
    print(user_perms[u]["name"], u)
    print(user_perms[u])