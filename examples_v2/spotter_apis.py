# This is a simple example of using the AI endpoints with Python.
# Thanks to Bill Back for the initial example
import requests
from requests.exceptions import HTTPError
import tomllib

from thoughtspot_rest_api_v1 import *

#
# Basic pattern for using Spotter / AI REST APIs:
# 1. Create Conversation with Model (formerly Worksheet) GUID to the Create Conversation endpoint
# 2. Provide Conversation ID and the same Model GUID to the Converse endpoint, along with a natural language question
# 3. Converse returns TML Search Tokens, which then you have to send into the /searchdata endpoint to get the data itself
#

with open("config.toml", "rb") as config_file:
    config = tomllib.load(config_file)

# Assign config to local values for ease of use.

# Login info
TS_URL = config["config"]["TS_URL"]
USERNAME = config["config"]["USERNAME"]
PASSWORD = config["config"]["PASSWORD"]
ORG_ID = config["config"]["ORG_ID"]

# GUID for the model to use.
MODEL_GUID = '{model_guid}'


def create_client() -> TSRestApiV2:
    """
    Creates a new API client.
    :return: A TSRestApiV2 client instance for making calls.
    """
    ts: TSRestApiV2 = TSRestApiV2(server_url=TS_URL)

    try:
        auth_token_response = ts.auth_token_full(username=USERNAME, password=PASSWORD,
                                                 org_id=ORG_ID, validity_time_in_sec=36000)
        ts.bearer_token = auth_token_response['token']

    except HTTPError as error:
        _bail_with_error(error)

    print('Created a client')
    return ts


def do_single_call(ts: TSRestApiV2) -> None:
    """
    Tests single call to get an answer via an API.
    :param ts: A TSRestApiV2 client instance for making calls that has already been authenticated.
    :return: None
    """
    print('Testing single call questions')

    resp = ts.ai_answer_create(metadata_identifier=MODEL_GUID,
                               query="give me a list of all the things I sold and how many of each")
    tokens = resp['tokens']

    search_data_resp = call_search_data_api(ts=ts, model_guid=MODEL_GUID, search_tokens=tokens)
    print_search_data(search_data_resp)


def do_conversation(ts: TSRestApiV2) -> None:
    """
    Tests having a data conversation.
    :param ts: A TSRestApiV2 client instance for making calls that has already been authenticated.
    :return: None
    """
    print('Testing a full conversation')

    try:
        conv_create_resp = ts.ai_conversation_create(metadata_identifier=MODEL_GUID)
        conversation_id = conv_create_resp['conversation_identifier']

        msg_1 = "show me the top 20 selling items for the west region"
        resp = ts.ai_conversation_converse(conversation_identifier=conversation_id,
                                           metadata_identifier=MODEL_GUID,
                                           message=msg_1)

        # The response has a list with one item (??) that has the details.
        search_data_resp = call_search_data_api(ts=ts, model_guid=MODEL_GUID, search_tokens=resp[0]['tokens'])
        print_search_data(search_data_resp)

        # follow-up questions
        msg_2 = "break these out by store"
        resp = ts.ai_conversation_converse(conversation_identifier=conversation_id,
                                           metadata_identifier=MODEL_GUID,
                                           message=msg_2)

        search_data_resp = call_search_data_api(ts=ts, model_guid=MODEL_GUID, search_tokens=resp[0]['tokens'])
        print_search_data(search_data_resp)

    except HTTPError as error:
        _bail_with_error(error)

# Untested at this time, future feature
'''
def do_decomposed_query(ts: TSRestApiV2) -> None:
    """
    Tests decomposed queries (whatever those are).
    :param ts: A TSRestApiV2 client instance for making calls that has already been authenticated.
    :return: None
    """
    print('Testing a decomposed query')

    # conversation ID is optional in this call.
    # conversation_id = ts.ai_conversation_create(metadata_identifier=RETAIL_SALES_WS)['conversation_identifier']

    # First, let's just use generically against a liveboard.
    endpoint = "ai/analytical-questions"  # endpoint for decomposing
    resp = ts.post_request(endpoint=endpoint, request={
        "liveboardIds": [
            "3f5d2d4b-87da-4f59-a144-85d444eada18"
        ]
    })

    print(resp)
'''

def _bail_with_error(error: requests.exceptions.HTTPError) -> None:
    """
    Prints info about the error and then exits.
    :param error:
    :return:
    """
    print(error)
    print(error.response.content)


def call_search_data_api(ts: TSRestApiV2, model_guid: str, search_tokens: str) -> List:
    """
    Uses the search data API to get the data and then prints the results.
    :param ts: The TSRestApiV2 client instance for making calls that has already been authenticated.
    :param model_guid: A valid data source GUID.
    :param search_tokens: The search tokens to use.
    :return: None
    """
    print(f'Searching data {search_tokens}')
    resp = ts.searchdata(
        {"logical_table_identifier": MODEL_GUID, "query_string": search_tokens, "record_size": 50})

    return resp


def print_search_data(search_data) -> None:
    """
    Prints the data from a 'searchdata' call.  This assumes it works.
    :param search_data: The response which has contents with the actual data.
    :return: None
    """
    # Extract the table contents from the API response
    contents = search_data['contents'][0]
    column_names = contents['column_names']
    data_rows = contents['data_rows']

    # Compute the maximum width for each column for proper alignment
    widths = []
    for i, header in enumerate(column_names):
        col_width = max(len(str(header)), max(len(str(row[i])) for row in data_rows))
        widths.append(col_width)

    # Create the header row and a separator row
    header_row = " | ".join(str(header).ljust(widths[i]) for i, header in enumerate(column_names))
    separator = "-+-".join("-" * widths[i] for i in range(len(widths)))
    table_width = len(header_row)

    # Separator for readability.
    print("")
    print("-" * table_width)
    print("")

    # Print the table to stdout
    print(header_row)
    print(separator)
    for row in data_rows:
        print(" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)))

    # Separator for readability.
    print("")
    print("-" * table_width)
    print("")


if __name__ == "__main__":
    print('Testing AI')

    tsapi = create_client()

    do_single_call(tsapi)

    do_conversation(tsapi)

    # do_decomposed_query(tsapi) # new feature not yet in this version.

    print('Testing complete')