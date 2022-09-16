import os
import json

from thoughtspot_rest_api_v1 import *


username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

ts: TSRestApiV1 = TSRestApiV1(server_url=server)
try:
    ts.session_login(username=username, password=password)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)

# V1 pinboarddata
# For retrieving the data from any viz on an existing Liveboard or a specific viz on it
# The endpoint is called 'pinboarddata' because historically Liveboards were called Pinboards
lb_guid = '{lbGuid}'
viz_on_lb_guid = '{vizGuid}'  # For retrieving from one specific viz

lb_data_response = ts.pinboarddata(pinboard_guid=lb_guid)

viz_data_response = ts.pinboarddata(pinboard_guid=lb_guid, vizids=[viz_on_lb_guid])

# Results are a List of objects
for viz_data in lb_data_response:
    # Do processing of the data
    print(json.dumps(viz_data, indent=2))  # just example to see the results

# Results are a List of objects
for viz_data in viz_data_response:
    # Do processing of the data
    print(json.dumps(viz_data, indent=2))  # just example to see the results

# V1 searchdata
# Search Data API allows an arbitrary 'TML Search String' to be passed to return results
# It uses a data source object, but not any existing Liveboard or Answer

ds_guid = '{dsGuid}'  # typically a Worksheet, but could be Table or View
tml_search_string = '[Product Name] [Sales] by [Region]'
search_data_response = ts.searchdata(query_string=tml_search_string, data_source_guid=ds_guid)


# V2 /data/ endpoints
# V2 allows you to retrieve JSON results from a Saved Answer
# As well as pull back the SQL query used by an Answer or the Vizes on a Liveboard

ts2: TSRestApiV2 = TSRestApiV2(server_url=server)
try:
    ts2.session_login(username=username, password=password)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)

answer_guid = '{answerGuid}'
answer_data_response = ts2.data_answer_data(guid=answer_guid)

answer_sql = ts2.data_answer_query_sql(guid=answer_guid)

all_lb_sql = ts2.data_liveboard_query_sql(guid=lb_guid)

viz_sql = ts2.data_liveboard_query_sql(guid=lb_guid, viz_ids=[viz_on_lb_guid])

for lb_sql in all_lb_sql:
    print(json.dumps(lb_sql, indent=2))

# You can also get data results in CSV and XSLX format using the V2 REST API when the viz is in a table format using
# the /report/ endpoints. See liveboard_pdf_export.pdf for those examples (as the same endpoints export PDF and PNG)
