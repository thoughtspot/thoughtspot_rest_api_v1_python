import os
import json
import requests.exceptions

from thoughtspot_rest_api_v1 import *


username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

ds_guid = '{dsGuid}'  # typically a Worksheet, but could be Table or View
tml_search_string = '[Product Name] [Sales] by [Region]'

answer_guid = '{answerGuid}'

lb_guid = '{lbGuid}'
viz_on_lb_guid = '{vizGuid}'  # For retrieving from one specific viz

# search_data_response = ts.searchdata(query_string=tml_search_string, data_source_guid=ds_guid)

ts: TSRestApiV2 = TSRestApiV2(server_url=server)
try:
    auth_token_response = ts.auth_token_full(username=username, password=password, validity_time_in_sec=3000)
    ts.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()


answer_request = {
    'metadata_identifier': answer_guid,
    'data_format': 'COMPACT',
    'record_offset': 0,
    'record_size': 10000  # default is 10
}
answer_data_response = ts.metadata_answer_data(request=answer_request)

answer_sql = ts.metadata_answer_sql(answer_identifier=answer_guid)

all_lb_request = {
    'metadata_identifier': lb_guid,
    'data_format': 'COMPACT',
    'record_offset': 0,
    'record_size': 10000  # default is 10
}
lb_data_response = ts.metadata_liveboard_data(request=all_lb_request)

all_lb_sql = ts.metadata_liveboard_sql(liveboard_identifier=lb_guid)

viz_sql = ts.metadata_liveboard_sql(liveboard_identifier=lb_guid, visualization_identifiers=[viz_on_lb_guid])

for lb_sql in all_lb_sql:
    print(json.dumps(lb_sql, indent=2))

# Results are a List of objects
for viz_data in lb_data_response:
    # Do processing of the data
    print(json.dumps(viz_data, indent=2))  # just example to see the results

# Results are a List of objects
for viz_data in lb_data_response:
    # Do processing of the data
    print(json.dumps(viz_data, indent=2))  # just example to see the results

search_data_request = {
    'query_string': tml_search_string,
    'logical_table_identifier': ds_guid,
    'data_format': 'COMPACT',
    'record_offset': 0,
    'record_size': 10000  # default is 10
}
search_data_response = ts.searchdata(request=search_data_request)

# You can also get data results in CSV and XSLX format using the V2 REST API when the viz is in a table format using
# the /report/ endpoints. See liveboard_pdf_export.pdf for those examples (as the same endpoints export PDF and PNG)
