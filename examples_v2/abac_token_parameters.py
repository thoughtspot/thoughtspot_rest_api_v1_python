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


# parameters : {name: value ... }
# filters: {{name}: [{values}... }
def create_jwt(parameters, filters, persist_all=False, version='9.11'):
    if version == '9.10':
        full_structure = {
            'jwt_user_options': {
                'parameters': []
            }
        }
        if len(parameters) > 0:
            runtime_param_section = {'runtime_param_override': {}}
            p_count = 1
            for param in parameters:
                cur_param_id = 'param{}'.format(p_count)
                cur_param_val_id = 'paramVal{}'.format(p_count)
                runtime_param_section['runtime_param_override'][cur_param_id] = param
                runtime_param_section['runtime_param_override'][cur_param_val_id] = parameters[param]
                p_count += 1
            # print(runtime_param_section)
            full_structure['jwt_user_options']['parameters'].append(runtime_param_section)
        if len(filters) > 0:
            runtime_filter_section = {'runtime_filter': {}}
            f_count = 1
            for fil in filters:
                cur_filter_col = 'col{}'.format(f_count)
                cur_filter_val_id = 'val{}'.format(f_count)
                cur_filter_op_id = 'op{}'.format(f_count)
                if len(filters[fil]) == 1:
                    cur_filter_op_value = 'EQ'
                else:
                    cur_filter_op_value = 'IN'
                runtime_filter_section['runtime_filter'][cur_filter_col] = fil
                runtime_filter_section['runtime_filter'][cur_filter_op_id] = cur_filter_op_value
                runtime_filter_section['runtime_filter'][cur_filter_val_id] = filters[fil]
                f_count += 1
            # print(runtime_filter_section)
            full_structure['jwt_user_options']['parameters'].append(runtime_filter_section)
    else:
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

    # Simple declaration of parameters as Key:Value
    params = {'Security': 'f65fee3a-75f4-4e6e-a801-995113566d68'}

    # Simple declaration of Filters as Key:[Values]
    # You can do all Runtime Filter types, but this handles all Attribute EQ/IN assignment, typical for RLS entitlements
    filters = {
        'Region': ["West", "Southwest"],
        "Product Type": ['Shirts', 'Swimwear']
    }

    jwt = create_jwt(parameters=params, filters=filters, version='9.10')

    auth_token_response = ts.auth_token_full(username=username, password=password, org_id=org_id,
                                             validity_time_in_sec=3000, additional_request_parameters=jwt)

    print(json.dumps(auth_token_response, indent=2))
    print(auth_token_response['token'])
    ts.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()


'''
Below are the formats for the JWT, which are encoded into the creator function

    # 9.10 pre-beta syntax
    jwt_9_10 = {
        'jwt_user_options': {
            'parameters': [
                {
                    'runtime_param_override': {
                        'param1': 'Security',
                        'paramVal1': "f65fee3a-75f4-4e6e-a801-995113566d68"
                    }
                },
                {
                    'runtime_filter': {
                        'col1': "Region",
                        'op1': "IN",
                        'val1': ["West", "Southwest"],
                        'col2': "Product Type",
                        'op2': "IN",
                        'val2': ['Shirts', 'Swimwear'],

                    }
                }
            ]
        }
    }

    jwt_9_11 = {
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