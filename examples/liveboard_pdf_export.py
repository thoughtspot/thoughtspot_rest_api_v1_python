import os
import requests.exceptions

# from thoughtspot_rest_api_v1 import *
from src.thoughtspot_rest_api_v1 import *

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

# V2 API endpoints with more options
ts2: TSRestApiV2 = TSRestApiV2(server_url=server)
try:
    ts2.session_login(username=username, password=password)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)

# V2 Allows export from an Answer vs. just a Liveboard
answer_guid = '{single_answer_guid}'

answer_export_pdf = ts2.report_answer(guid=answer_guid, report_type=ReportTypes.PDF)
with open('pdf_answer_test.pdf', 'wb') as fh:
    fh.write(answer_export_pdf)

answer_export_png = ts2.report_answer(guid=answer_guid, report_type=ReportTypes.PNG)
with open('png_answer_test.png', 'wb') as fh:
    fh.write(answer_export_png)

answer_export_csv = ts2.report_answer(guid=answer_guid, report_type=ReportTypes.CSV)
with open('csv_answer_test.csv', 'wb') as fh:
    fh.write(answer_export_csv)

answer_export_xlsx = ts2.report_answer(guid=answer_guid, report_type=ReportTypes.XLSX)
with open('xlsx_answer_test.xlsx', 'wb') as fh:
    fh.write(answer_export_xlsx)

# More options to export from Liveboard, although still bound by the same contraints

lb_guid = '{lb_guid}'
viz_on_lb_guid = '{viz_guid}'  # CSV and XLSX only export from a Viz that is a table (no charts)

# Whole Liveboard
whole_lb_pdf = ts2.report_liveboard(guid=lb_guid, report_type=ReportTypes.PDF, landscape_or_portrait='PORTRAIT',
                                    logo=False)  # Many additional options for formatting

# Specific Viz on Liveboard
one_viz_pdf = ts2.report_liveboard(guid=lb_guid, report_type=ReportTypes.PDF, viz_ids=[viz_on_lb_guid])

one_viz_csv = ts2.report_liveboard(guid=lb_guid, report_type=ReportTypes.CSV, viz_ids=[viz_on_lb_guid])

one_viz_xlsx = ts2.report_liveboard(guid=lb_guid, report_type=ReportTypes.XLSX, viz_ids=[viz_on_lb_guid])
