#
# Set of scripts showing:
# (1) How to set obj_id on objects + export TML with obj_id instead of GUID
# (2) Scripts for generating automatic obj_ids from existing objects that do not have them
# to build out a mapping of GUID:obj_id to generate the update REST API commands
#

import json
import os
import requests.exceptions
from typing import Optional, Dict, List
from urllib import parse
import re
from collections import Counter

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

# Simple example of setting a single obj_id on a known GUID
def set_one_object():
    resp = ts.metadata_update_obj_id(new_obj_id='Conn.DB_Name.TableName', guid='43ab8a16-473a-44dc-9c78-4346eeb51f6c')
    print(json.dumps(resp, indent=2))

# Simple example of setting multiple at once using the full request format
def set_multiple_objects():
    req = {
        "metadata": [
            {
                "new_obj_id": "Table_A",
                "metadata_identifier": "43ab8a16-473a-44dc-9c78-4346eeb51f6c"
            },
            {
                "new_obj_id": "Table_B",
                "metadata_identifier": "4346eeb51f6c-9c78-473a-44dc-43ab8a16"
            },
        ]
    }

    resp = ts.metadata_update_obj_id(request_override=req)
    print(json.dumps(resp, indent=2))

# Build out full request from simple GUID:obj_id Dict
def build_multiple_objects_update_request_by_guid(guid_obj_id_map: Dict):
    req = {
        "metadata": []
    }
    for g in guid_obj_id_map:
        req["metadata"].append(
            {"metadata_identifier": g,
             "new_obj_id": guid_obj_id_map[g]}
        )
    return req

# Build out full request from simple current_obj_id:new_obj_id Dict
def build_multiple_objects_update_request_by_obj_id(cur_obj_id_new_obj_id_map: Dict):
    req = {
        "metadata": []
    }
    for c in cur_obj_id_new_obj_id_map:
        req["metadata"].append(
            {"current_obj_id": c,
             "new_obj_id": cur_obj_id_new_obj_id_map[c]}
        )
    return req

# Wrapper of Export TML of a single item, with lookup via GUID or obj_id, and saving to disk with
# standard naming pattern
def export_tml_with_obj_id(guid:Optional[str] = None,
                           obj_id: Optional[str] = None,
                           save_to_disk=True):
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
            obj_id = tables[0]['metadata_header']['objId']

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

    # Get obj_id from the TML
    lines = yaml_tml[0]['edoc'].splitlines()
    if obj_id is None:
        if lines[0].find('obj_id: ') != -1:
            obj_id = lines[0].replace('obj_id: ', "")

    obj_type = lines[1].replace(":", "")

    if save_to_disk is True:
        print(yaml_tml[0]['edoc'])
        print("-------")

        # Save the file with {obj_id}.{type}.{tml}
        filename = "{}.{}.tml".format(obj_id, obj_type)
        with open(file=filename, mode='w') as f:
            f.write(yaml_tml[0]['edoc'])

    return yaml_tml


#
# Objects may have null obj_ids or will have the GUID attached on the auto-generated obj_id
# To standardize for using across the entire set of Orgs, you'll need to create your own naming patterns
# This shows retrieving all the objects and using either Table Attributes or Name to generate unique obj_id
#
def retrieve_dev_org_objects_for_mapping(org_name: Optional[str] = None, org_id: Optional[int] = None):

    if org_id is None:
        org_req = {
            "org_identifier": org_name
        }
        org_resp = ts.orgs_search(request=org_req)
        if len(org_resp) == 1:
            org_id = org_resp[0]["id"]
        else:
            raise Exception("No org with that org_name was found, please try again or provide org_id")

    ts2 = TSRestApiV2(server_url=server)
    try:
        auth_token_response = ts2.auth_token_full(username=username, password=password,
                                                 validity_time_in_sec=3000, org_id=org_id)
        ts.bearer_token = auth_token_response['token']
    except requests.exceptions.HTTPError as e:
        print(e)
        print(e.response.content)
        exit()

    types = ["LOGICAL_TABLE", "LIVEBOARD", "ANSWER"]
    search_req = {
        "record_offset": 0,
        "record_size": -1,
        "include_headers": True,
        "include_details": True,
        "metadata":[
            {"type": "LOGICAL_TABLE"},{"type": "LIVEBOARD"},{"type": "ANSWER"}
        ]
        ,
        "sort_options": {
            "field_name": "CREATED",
            "order": "DESC"
        }
    }

    conn_req = {
        "record_offset": 0,
        "record_size": -1,
        "include_headers": False,
        "include_details": False,
        "metadata": [
            {
                "type": "CONNECTION"
            }
        ]
        ,
        "sort_options": {
            "field_name": "CREATED",
            "order": "DESC"
        }
    }

    # Tables - split out Worksheets/ Models / Views from actual Table Objects
    try:
        tables_resp = ts2.metadata_search(request=search_req)
    except requests.exceptions.HTTPError as e:
        print(e)
        print(e.response.content)
        exit()

    # Connection names for mapping and use in obj_id naming schema for Tables
    try:
        conn_resp = ts2.metadata_search(request=conn_req)
    except requests.exceptions.HTTPError as e:
        print(e)
        print(e.response.content)
        exit()

    conn_map = {}
    for conn in conn_resp:
        # Create URL safe portion of obj_id for Connection
        # Assuming No Duplicate Connection Names in Org (fix this first if you don't have)
        # Define whatever automatic transformations to create URL safe
        # but aesthetically pleasing first transform from the existing object names
        c_obj_id = conn["metadata_name"].replace(" ", "")
        c_obj_id = parse.quote(c_obj_id)
        # obj_id = obj_id.replace("%3A", "_")
        # After parse quoting, there characters are in form %XX , replace with _ or blank space
        c_obj_id = re.sub(r"%..", "", c_obj_id)
        conn_map[conn["metadata_id"]] = c_obj_id
    # print(json.dumps(tables_resp, indent=2))

    final_guid_obj_id_map = {}

    for table in tables_resp:
        ds_type = table["metadata_header"]["type"]

        guid = table["metadata_id"]

        # Special property for certain system items that exist across all orgs - skip, cannot reset except in Org 0
        if "belongToAllOrgs" in table["metadata_header"]:
            if table["metadata_header"]["belongToAllOrgs"] is True:
                continue

        # Real tables
        if ds_type in ['ONE_TO_ONE_LOGICAL']:
            detail = table["metadata_detail"]
            db_table_details = detail["logicalTableContent"]["tableMappingInfo"]

            # Assumes a "{db}__{schema}__{tableName}" naming convention, but
            # {tsConnection}__{table} may make more sense across a number of Orgs with identical 'schemas' with
            # differing names
            # Essentially you want identical, unique obj_id for "the same table" across Orgs
            obj_id = "{}__{}__{}".format(db_table_details["databaseName"], db_table_details["schemaName"],
                                         db_table_details["tableName"])
        else:
            # For non-table objects, obj_ids just need to be URL safe strings
            # This is an example of a basic transformation from the Display Name to a URL safe string
            obj_id = table["metadata_name"].replace(" ", "_")   # Need more transformation
            obj_id = parse.quote(obj_id)
            # After parse quoting, there characters are in form %XX , replace with _ or blank space
            obj_id = re.sub(r"%..", "", obj_id)

        final_guid_obj_id_map[guid] = obj_id

    # print(json.dumps(final_guid_obj_id_map, indent=2))

    return final_guid_obj_id_map


#
# Looks at a guid:obj_id mapping and discovers any duplicate obj_ids generated by the initial auto-generation
#
def find_duplicate_obj_ids(initial_map: Dict) -> Dict:
    cnt = Counter(initial_map.values())

    if len(initial_map) == len(cnt):
        return {}
    else:
        duplicate_obj_ids = []
        for c in cnt:
            if cnt[c] > 1:
                duplicate_obj_ids.append(c)
        dup_map = {}

        for m in initial_map:
            if initial_map[m] in duplicate_obj_ids:
                dup_map[m] = initial_map[m]
        return dup_map
