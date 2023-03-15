import os
import requests.exceptions

from thoughtspot_rest_api_v1 import *


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

# V2 Allows export from an Answer vs. just a Liveboard
answer_guid = '{single_answer_guid}'
answer_request = {
    'metadata_identifier': answer_guid,
    'file_format': ReportTypes.PDF
}
answer_export_pdf = ts.report_answer(request=answer_request)
with open('pdf_answer_test.pdf', 'wb') as fh:
    fh.write(answer_export_pdf)

answer_request = {
    'metadata_identifier': answer_guid,
    'file_format': ReportTypes.PNG
}
answer_export_png = ts.report_answer(request=answer_request)
with open('png_answer_test.png', 'wb') as fh:
    fh.write(answer_export_png)

answer_request = {
    'metadata_identifier': answer_guid,
    'file_format': ReportTypes.CSV
}
answer_export_csv = ts.report_answer(request=answer_request)
with open('csv_answer_test.csv', 'wb') as fh:
    fh.write(answer_export_csv)


# More options to export from Liveboard, although still bound by the same constraints

lb_guid = '{lb_guid}'
viz_on_lb_guid = '{viz_guid}'  # CSV and XLSX only export from a Viz that is a table (no charts)

# Whole Liveboard - see Playground for additional parameters you can set under pdf_options
liveboard_request = {
    'metadata_identifier': lb_guid,
    'file_format': ReportTypes.PDF,
    'pdf_options': {
        'include_cover_page': False,
        'include_page_number': True
    }
}
whole_lb_pdf = ts.report_liveboard(request=liveboard_request)  # Many additional options for formatting
with open('whole_lb_test.pdf', 'wb') as fh:
    fh.write(whole_lb_pdf)

# Specific Viz on Liveboard
viz_request = {
    'metadata_identifier': lb_guid,
    'visualization_identifiers': [viz_on_lb_guid],
    'file_format': ReportTypes.PDF
}
one_viz_pdf = ts.report_liveboard(request=viz_request)
with open('one_viz_test.pdf', 'wb') as fh:
    fh.write(one_viz_pdf)

viz_request = {
    'metadata_identifier': lb_guid,
    'visualization_identifiers': [viz_on_lb_guid],
    'file_format': ReportTypes.CSV
}
one_viz_csv = ts.report_liveboard(request=viz_request)
with open('one_viz_test.csv', 'wb') as fh:
    fh.write(one_viz_csv)

