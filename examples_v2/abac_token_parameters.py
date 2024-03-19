import os
import requests.exceptions
import json

from thoughtspot_rest_api_v1 import *

#
# Script for implementing the upcoming ABAC / JWT capabilities of the V2.0 Full Access Token REST API
#
#

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

org_id = 0  # Set to org_id in multi-tenant environment

ts: TSRestApiV2 = TSRestApiV2(server_url=server)

# Simple function for translating {key: List} arguments into the full ABAC syntax for Full Access Token
# parameters : {name: value ... }
# filters: {{name}: [{values}... }
def create_abac_section(parameters, filters, persist_all=False):

    full_structure = {
        'user_parameters': {}
    }
    if len(parameters) > 0:
        runtime_param_section = {'parameters': []}
        # p_count = 1
        for param in parameters:
            cur_param = {'name': param, 'values': parameters[param], 'persist': persist_all}
            runtime_param_section['parameters'].append(cur_param)
        # print(runtime_param_section)
        full_structure['user_parameters'].update(runtime_param_section)
    if len(filters) > 0:
        runtime_filter_section = {'runtime_filters': []}
        for fil in filters:
            if len(filters[fil]) == 1:
                op = 'EQ'
            else:
                op = 'IN'
            cur_filter = {'column_name': fil, 'operator': op, 'values': filters[fil], 'persist': persist_all}

            runtime_filter_section['runtime_filters'].append(cur_filter)
        full_structure['user_parameters'].update(runtime_filter_section)
        # print(runtime_filter_section)

    return full_structure


try:

    # Simple declaration of parameters as Key:[Value], even though parameters are single-value at this time
    params = {'Security': ['f65fee3a-75f4-4e6e-a801-995113566d68']}

    # Simple declaration of Filters as Key:[Values]
    # You can do all Runtime Filter types, but this handles all Attribute EQ/IN assignment, typical for RLS entitlements
    filters = {
        'Region': ["West", "Southwest"],
        "Product Type": ['Shirts', 'Swimwear']
    }

    # This creates simple IN runtime filters from the provided structures above
    # See below in the comments for the full syntax, if you need to create other filter types directly
    # Choose persist_all=True when using Cookie-Based Trusted Auth; if False, use Cookieless
    user_parameters = create_abac_section(parameters=params, filters=filters, persist_all=False)

    auth_token_response = ts.auth_token_full(username=username, password=password, org_id=org_id,
                                             validity_time_in_sec=3000, additional_request_parameters=user_parameters)

    print(json.dumps(auth_token_response, indent=2))
    print(auth_token_response['token'])
    ts.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()


'''
Below are the formats for the ABAC portion of the Full Access Token, which are encoded into the creator function

abac_user_parameters = {
    'user_parameters': {
      "runtime_filters": [
        {
          "column_name": "Region",
          "operator": "IN",
          "values": ["West", "Southwest"],
          "persist": False
        },
        {
          "column_name": "Product Type",
          "operator": "IN",
          "values": ["Shirts", "Swimwear"],
          "persist": False
        }
      ],
      "parameters": [
        {
          "name": "Security",
          "values": ["f65fee3a-75f4-4e6e-a801-995113566d68"],
          "persist": False
        }
      ]
    }
}

'''