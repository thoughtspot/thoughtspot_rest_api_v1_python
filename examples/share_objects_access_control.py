import os
import json

from thoughtspot_rest_api_v1 import *


# You are probably better off looking at https://github.com/thoughtspot/cs_tools for more complete versions of this
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

read_only_guids = ['{group1Guid}', '{group2Guid}']
edit_guids = ['{guid4Guid']
lb_guid = 'lbGuid'

# Add sharing permissions
perms = ts.create_share_permissions(read_only_users_or_groups_guids=read_only_guids,
                                    edit_access_users_or_groups_guids=edit_guids)
ts.security_share(shared_object_type=TSTypes.LIVEBOARD, shared_object_guids=[lb_guid], permissions=perms)

# Remove sharing
guids_to_remove_sharing_from = ['{groupGuid6}', '{groupGuid7}']
remove_perms = ts.create_share_permissions(remove_access_users_or_groups_groups=guids_to_remove_sharing_from)
ts.security_share(shared_object_type=TSTypes.LIVEBOARD, shared_object_guids=[lb_guid],
                  permissions=remove_perms)

viz_guid = '{vizGuid}'
ts.security_shareviz(shared_object_type=TSTypes.LIVEBOARD, pinboard_guid=lb_guid, viz_guid=viz_guid,
                     principal_ids=read_only_guids)

# Check the set permissions
ts.security_metadata_permissions_by_id(object_type=TSTypes.LIVEBOARD, object_guid=lb_guid, dependent_share=False,
                                       permission_type=PermissionTypes.EFFECTIVE)

ts.security_effectivepermissionbulk(ids_by_type={MetadataTypes.LIVEBOARD: ['{lbGuid1}'],
                                                 MetadataTypes.ANSWER: ['{aGuid1}']}
                                    )

#
# REST API V2 simplifies down to a request from the principle (user or group) perspective or
# from the object perspective
#
ts2 = TSRestApiV2(server_url='https://a.thoughtspot.cloud')
try:
    ts2.session_login(username=username, password=password)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)

principal_perms = ts2.security_permission_principal(username_or_group_name='auser@domain.com')  # alternatively username_or_group_guid=

object_perms = ts2.security_permission_tsobject(guid=lb_guid, object_type=TSTypesV2.LIVEBOARD, include_dependents=False)