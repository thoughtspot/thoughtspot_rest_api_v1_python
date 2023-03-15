import os
import requests.exceptions

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


liveboards = ts.metadata_list(object_type=TSTypes.LIVEBOARD, filter='{Liveboard Name}')
# metadata_list returns an object with 'headers' key, that has the array of header objects about the returned list
first_liveboard_id = liveboards['headers'][0]["id"]
first_liveboard_name = liveboards['headers'][0]["name"]
print("First Pinboard Name: {}".format(first_liveboard_name))
print("First Pinboard ID: {}".format(first_liveboard_id))
try:
    liveboard_pdf = ts.export_pinboard_pdf(pinboard_id=first_liveboard_id, footer_text="Viz by the foot",
                                           cover_page=False, filter_page=False, landscape_or_portrait='PORTRAIT')
    new_file_name = "../Test PDF.pdf"
    with open(new_file_name, 'bw') as fh:
        fh.write(liveboard_pdf)
except requests.exceptions.HTTPError as e:
    print(e)

ts.session_logout()

# See examples_v2 directory for V2 Endpoints with additional options
