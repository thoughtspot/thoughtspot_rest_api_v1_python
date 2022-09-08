import os
import requests.exceptions
import json

from thoughtspot_rest_api_v1 import *


#
# This example uses the connection APIs to
# Some of these APIs are not part of the tspublic/v1/ path at the moment,
# but they are used within the ThoughtSpot UI and are accessible to users
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

# Connection to update
connection_guid = '3289e6da-80ec-41c3-a8f9-16fc018e2355'

# If you do not have the GUID, use to find by name
#connections = ts.tsrest.metadata_listobjectheaders(object_type=MetadataNames.CONNECTION, filter='Connection Name')

# metadata/details provides the connection_config needed for the connection/create and connection/update commands
connection_details = ts.metadata_details(object_type=MetadataNames.CONNECTION, object_guids=[connection_guid])

# These helper functions parse out the parts you need from very complex connection_details object
connection_config = ts.get_connection_config_from_metadata_details(connection_details)
connection_name = ts.get_connection_name_from_metadata_details(connection_details)
connection_type = ts.get_connection_type_from_metadata_details(connection_details)

# connection/fetchConnection is currently non-public API used to retrieve all details of objects (database, schema, table)
# it does not pull back columns for every object without special flag (no need to use
fetch_connection_response = ts.connection_fetch_connection(connection_guid=connection_guid,
                                                           config_json_string=json.dumps(connection_config))

# We'll manipulate the 'externalDatabases' portion of the connection/fetchConnection response
external_dbs = fetch_connection_response['externalDatabases']

# Two helper functions for pulling all of the databases and schemas, in the format for adding tables
#db_list = ts.tsrest.get_databases_from_connection(external_databases_from_fetch_connection=external_dbs)

dbs_with_schemas = ts.get_databases_and_schemas_from_connection(external_databases_from_fetch_connection=external_dbs,
                                                                schema_names_to_skip=['INFORMATION_SCHEMA'])

# Early break if you want to just see the listing of all databases and schemas within
# print(dbs_with_schemas)
# exit()

# We'll define an object with the database, schema and particular tables (or bring them all in), that matches the
# format of the output of get_databases_and_schemas_from_connection

# tables_to_add_map format =  { 'database_name' : { 'schema_name' : ['table_name_1', 'table_name_2']}
# tables_to_add_map format to bring in all tables = { 'database_name' : { 'schema_name' : [] }

to_add_map = { 'Database A': {'Schema 1': []}}  # This will add every table in Database A, Schema 1

# get_selected_tables_from_connection parses down the externalDatabases response to only include schemas with
# existing imported tables or un-imported schemas we are adding tables to for the first time
selected_external_databases = ts.get_selected_tables_from_connection(external_databases_from_fetch_connection=external_dbs,
                                                                     tables_to_add_map=to_add_map)

# ThoughtSpot will never return the password in a response, but you may need it to do the update
connection_config['password'] = os.getenv('connection_password')        # or type in yourself

# add_new_tables_to_connection uses the tables_to_add_map to request the columns for any new table.
# It outputs the full object to be serialized into the metadata_json
update_metadata_obj = ts.add_new_tables_to_connection(selected_external_databases=selected_external_databases,
                                                      tables_to_add_map=to_add_map,
                                                      connection_guid=connection_guid,
                                                      config_json=connection_config
                                                     )
# If you want to see the completed
# print(json.dumps(update_msg, indent=2))

# Send the connection/update REST API command. Remember to use json.dumps() on the update_metadata_obj
update_response = ts.connection_update(connection_guid=connection_guid, connection_name=connection_name,
                                       connection_type=connection_type, metadata_json=json.dumps(update_metadata_obj),
                                       create_without_tables=True)
# On 7.1.1 or earlier Software releases, you can use the internal endpoint to access connection APIs that are
# public in current Cloud releases. At some point this won't be necessary

#update_response = ts.tsrest.connection_update(connection_guid=connection_guid, connection_name=connection_name,
#                                              connection_type=connection_type, metadata_json=json.dumps(update_metadata_obj),
#                                              create_without_tables=False, use_internal_endpoint=True)
# If you are creating a connection for the first time, current ThoughtSpot Cloud releases allow you to
# create the connection without bringing in a table.
# ThoughtSpot Software releases (7.1.1 and earlier), you must bring in at least 1 table when creating a connection.
# This limitation exists both in the UI and the APIs.
# The metadata_json for the connection/create endpoint is the same as connection/update
# Although you need the Connection to exist and be saved to use connection_fetch_connection()
# So your best practice is to manually create at least one Connection initially that you can use to pull the details

