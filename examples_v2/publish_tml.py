import os
import requests.exceptions

from src.thoughtspot_rest_api_v1 import *

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


# Manipulating the properties of TML files is best accomplished with the thoughtspot_tml library
# https://github.com/thoughtspot/thoughtspot_tml


def get_tml_string_placeholder() -> str:
    # This example assumes you have a TML file (YAML version) as a string.
    # See the examples in thoughtspot_tml repository of how open, manipulate, and dump back to YAML TML string
    pass

tml_string_1 = get_tml_string_placeholder()
# You can import any number of TMLs at once. The response will be in the order that you import
# It is best practice to upload all Data Model objects (Tables, Worksheets, Views) together so that any
# references to new objects will be interpreted as part of the uploaded set of TMLs
# (otherwise existing other objects will be searched for name matching)
tml_import_response = ts.metadata_tml_import(metadata_tmls=[tml_string_1], import_policy='PARTIAL', create_new=False)

new_guids_in_order = []
# response is an Array / List
for i in tml_import_response:
    new_guid = i['response']['header']['id_guid']
    new_guids_in_order.append(new_guid)
    tml_import_status_code = i['response']['status']['status_code']
    if tml_import_status_code in ['WARNING', 'ERROR']:
        error_msg = tml_import_status_code = i['response']['status']['error_message']

# Two next steps:
# 1. Record a mapping of original uploaded GUIDs to the newly created object GUIDs, to allow later updates from original file
# 2. Share the newly create objects to a Group or User. See 'share_objects_access_control.py' for example code
