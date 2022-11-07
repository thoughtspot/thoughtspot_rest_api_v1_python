import os
import requests.exceptions
import json

from thoughtspot_rest_api_v1 import *

#
# Short script to show how to use the connection_create and connection_update commands
# Documentation on exact properties / options: https://developers.thoughtspot.com/docs/?pageid=connections-api#connection-metadata
#

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

ts: TSRestApiV1 = TSRestApiV1(server_url=server)
try:
    ts.session_login(username=username, password=password)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)


# You should instead implement the secure retrieval of the password for the connection
def securely_retrieve_connection_pw():
    conn_pw = os.getenv('connection_password')
    return conn_pw


# See the connection types possible if you need them. 'name' is what is used in the connection_type= of create/update
conn_types = ts.connection_types()
for conn_type in conn_types:
    print(conn_type['name'], conn_type['displayName'])

# The actual properties of the connection are set using the connection metadata
# https://developers.thoughtspot.com/docs/?pageid=connections-api#connection-metadata
connection_metadata = {
    'accountName': 'myAccountName',
    'user': 'myUser',
    'password': securely_retrieve_connection_pw(),
    'role': 'yourRole',
    'warehouse': 'SnowflakeWarehouse'
}
# Convert the dict into a JSON string
conn_json = json.dumps(connection_metadata)
# Create the connection. use_internal_endpoint=True for software versions prior to 7.1
response = ts.connection_create(connection_name='My Great Connection', connection_type="RDBMS_SNOWFLAKE",
                                metadata_json=conn_json, description='Connection Descr',
                                create_without_tables=True, use_internal_endpoint=False)

new_connection_guid = response['header']['id']

# connection_update uses basically the same form, but you specify the GUID of the existing connection to update
ts.connection_update(connection_guid=new_connection_guid,
                     connection_name='My Even Greater Connection', connection_type="RDBMS_SNOWFLAKE",
                     metadata_json=conn_json, description='Connection Descr 2',
                     create_without_tables=True, use_internal_endpoint=False)
