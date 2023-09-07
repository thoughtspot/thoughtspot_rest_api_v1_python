import os
import json
import requests

from thoughtspot_rest_api_v1 import *

# Script to show using the /admin/ endpoints around Custom Actions
# Specific use-case shown is making an Action available on Context Menu of every viz on a Liveboard

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

ts: TSRestApiV1 = TSRestApiV1(server_url=server)
try:
    ts.session_login(username=username, password=password)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)

# Code snippet to lookup a custom action's GUID
def find_action_guid(display_name_to_find: str = None, action_js_id_to_find: str = None) -> str:
    # Custom Actions are controlled by methods under the /admin/actions/ endpoint root
    existing_actions = ts.admin_embed_actions()

    # /admin/embed-actions returns an array of objects. Each has 'id', 'name' and then ['detail']['function'] as the JS id
    # display_name_to_find = "Example Global action"
    # action_js_id_to_find = "example-global-action"

    if display_name_to_find is not None:
        for a in existing_actions:
            if a['name'] == display_name_to_find:
                return a['id']

    if action_js_id_to_find is not None:
        for a in existing_actions:
            if a['detail']['function'] == action_js_id_to_find:
                return a['id']

    # if neither returns
    print("Could not find action matching name: {} or js_id {}".format(display_name_to_find, action_js_id_to_find))
    return ""


# If you know set of action GUIDs to associate to, provide list here to skip lookups
action_guids = []


# The action_associations_post endpoint allows for APPENDS, so you do not need any of this information
# Simply provided as example of calls if you do want to get the specific details
# action_info = ts.admin_embed_action(action_guid=action_guid)
# print(json.dumps(action_info, indent=2))

# Existing association info will appear under 'actionAssociationMap' key
# print(json.dumps(action_info['actionAssociationMap'], indent=2))

# To associate all Vizes on a Liveboard, use either /metadata/listvizheaders or /metadata/tml/export
lb_guids = ['c7366d05-dc19-4aae-8f72-e8acf1d641e1']

internal_viz_guids_to_add_to_action = []

for lb_guid in lb_guids:
    # viz_headers = ts.metadata_listvizheaders(guid=lb_guid)
    viz_guids_to_add_to_action = []
    # TML can be parsed to give you info like chart.type, to skip KPI charts or otherwise with assignment
    # Or to find any formulas defined at the viz level, which might also be reason to skip
    lb_tml_obj = ts.metadata_tml_export(guid=lb_guid, export_fqn=True)

    for v in lb_tml_obj['liveboard']['visualizations']:
        viz_guid = v['viz_guid']
        print(viz_guid)
        # Not every viz has 'answer' key, could be 'note_tile' now
        if 'answer' in v:
            chart_type = v['answer']['chart']['type']
            print(chart_type)
            if chart_type not in ['KPI']:
                # Skip any with a formula defined
                if 'formulas' not in v['answer']:
                    viz_guids_to_add_to_action.append(viz_guid)

    print("Viz GUIDs to add to action: ")
    print(viz_guids_to_add_to_action)

    # The Custom Actions APIs use another GUID, different from the viz_guids seen in TML
    # You must call /metadata/details and find the refAnswerBook.id
    # ['storables'][0]["reportContent"]["sheets"][0]["sheetContent"]["visualizations"]
    # ['storables'][0]["reportContent"]["sheets"][0]["sheetContent"]["visualizations"][0]["vizContent"]["refAnswerBook"]["id"]
    # where the ['storables'][0]["reportContent"]["sheets"][0]["sheetContent"]["visualizations"][0]['header']['id']
    # matches to the viz_id

    # Container for the internal 'refAnswerBook' viz ids used by the Actions

    details = ts.metadata_details(object_type=TSTypes.LIVEBOARD, object_guids=[lb_guid])

    # /metadata/details is very complex structure, this gets to the part with info on the visualizations
    vizes = details['storables'][0]["reportContent"]["sheets"][0]["sheetContent"]["visualizations"]
    for v in vizes:
        internal_id = v["vizContent"]["refAnswerBook"]["id"]
        external_viz_guid = v['header']['id']
        if external_viz_guid in viz_guids_to_add_to_action:
            internal_viz_guids_to_add_to_action.append(internal_id)

for action_guid in action_guids:
    #
    # Format for actionAssociationMap is something like:
    #

    # 'actionAssociationMap' : { 'VISUALIZATION' :
    #                               { '{viz_id_1}' : {
    #                                       'context': 'CONTEXT_MENU',
    #                                        'enabled': 'true'
    #                                    }


    #
    action_info = { 'actionAssociationMap' : { 'VISUALIZATION' : {} } }

    # To add a new Context Menu association, do:
    # new_viz_to_assoc = '{new_viz_id}'
    # action_info['actionAssociationMap']['VISUALIZATION'][new_viz_to_assoc] = {
    #    "context": "CONTEXT_MENU",
    #    "enabled": "true"
    # }

    # Update the actionAssociationMap to set all the identified viz IDs to be on the context menu
    for guid in internal_viz_guids_to_add_to_action:
        action_info['actionAssociationMap']['VISUALIZATION'][guid] = {
            "context": "CONTEXT_MENU",
            "enabled": "true"
        }

    # Update the action associations using /admin/embed/actions/{}/associations
    resp = ts.admin_embed_action_associations_post(action_guid=action_guid, action_association=action_info)
    print(resp)