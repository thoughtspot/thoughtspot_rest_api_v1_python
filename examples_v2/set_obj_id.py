import json
import os
import requests.exceptions
from typing import Optional, Dict, List

from src.thoughtspot_rest_api_v1 import TSRestApiV2, TSTypesV2, ReportTypes, TSRestApiV1

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself
org_id = 0

ts = TSRestApiV2(server_url=server)
try:
    auth_token_response = ts.auth_token_full(username=username, password=password,
                                               validity_time_in_sec=3000, org_id=org_id)
    ts.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

def create_obj_id_update_request(guid: str, obj_id: str):
    update_req = {
        "headers_update":
            (
                {'identifier': guid,
                 'attributes': (
                     {
                         'name': 'obj_id',
                         'value': obj_id
                     }
                 )
                 }
            )
    }
    return update_req

# { 'guid' : 'obj_id' }
def create_multi_obj_id_update_request(guid_obj_id_map: Dict):
    update_req = {
        "headers_update": []
    }
    for guid in guid_obj_id_map:
        header_item = {
            'identifier': guid,
            'attributes': (
                 {
                     'name': 'obj_id',
                     'value': guid_obj_id_map[guid]
                 }
            )
         }
        update_req["headers_update"].append(header_item)

    return update_req

def set_one_object():
    # Simple example of setting a Table object to have a Full Qualified Name as the obj_id
    update_req = create_obj_id_update_request(guid='43ab8a16-473a-44dc-9c78-4346eeb51f6c', obj_id='Conn.DB_Name.TableName')

    resp = ts.metadata_headers_update(request=update_req)
    print(json.dumps(resp, indent=2))


def export_tml_with_obj_id(guid:Optional[str] = None, obj_id: Optional[str] = None):
    # Example of metadata search using obj_identifier (the property may be updated?)
    if obj_id is not None:
        search_req = {
            "metadata": (
                {'obj_identifier': obj_id}
            ),
            "sort_options": {
                "field_name": "CREATED",
                "order": "DESC"
            }
        }

        tables = ts.metadata_search(request=search_req)
        if len(tables) == 1:
            guid = tables[0]['metadata_id']

        # print(json.dumps(log_tables, indent=2))

    if guid is None:
        raise Exception()

    # export_options allow shifting TML export to obj_id, without any guid references
    exp_opt = {
        "include_obj_id_ref": True,
        "include_guid": False,
        "include_obj_id": True
    }


    yaml_tml = ts.metadata_tml_export(metadata_ids=[guid], edoc_format='YAML',
                                      export_options=exp_opt)
    print(yaml_tml[0]['edoc'])
    print("-------")

    # Save the file with {obj_id}.{type}.{tml}
    filename = "{}.table.tml".format(table['metadata_header']['objId'])
    with open(file=filename, mode='w') as f:
        f.write(yaml_tml[0]['edoc'])