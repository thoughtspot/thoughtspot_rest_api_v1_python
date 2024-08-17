import os
import requests.exceptions
import json

from src.thoughtspot_rest_api_v1 import *

#
# Example of deploying from a pre_prod or release branch out to individual customer "prod Orgs"
# There are two patterns for this:
#  (1) Use the Deploy API from the single pre_prod branch to each Org
#  (2) Create pull requests to the branch for each "prod Org", then use Deploy API from those branches into their
#      linked "org" (environment). The second pattern is only necessary when additional TML modification is required
#      only for the final environment - an example would be changing Alias names or RLS rules specific to each customer
#

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

branch_name_to_deploy_from = "pre_prod"

org_names_to_deploy_to = [
    "cust_a",
    "cust_b"
]

# Must log into Primary / Org 0 to get the list of Orgs, to get their org_id properties
org0: TSRestApiV2 = TSRestApiV2(server_url=server)
try:
    auth_token_response = org0.auth_token_full(username=username, password=password,
                                               validity_time_in_sec=3000, org_id=0)
    org0.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

for org_name in org_names_to_deploy_to:
    org_search_req = {
        "org_identifier": org_name
    }
    search_resp = org0.orgs_search(request=org_search_req)
    if len(search_resp) == 1:
        org_id = search_resp[0]['id']

        # Create bearer token for the org matching the org name
        ts: TSRestApiV2 = TSRestApiV2(server_url=server)
        try:
            auth_resp = ts.auth_token_full(username=username, password=password,
                                           validity_time_in_sec=3000, org_id=org_id)
            ts.bearer_token = auth_resp['token']
        except requests.exceptions.HTTPError as e:
            print(e)
            print(e.response.content)
            exit()

        # This shows Pattern 1, to deploy from a single "pre_prod" branch. Match org_name to branch name
        # or do a more complex mapping if you needed to do a PR to each branch and make final adjustments to TML
        deploy_req = {
          "branch_name": branch_name_to_deploy_from,   # use the org_name if you make PR to each branch vs. 1 pre_prod
          "deploy_type": "DELTA",  # Switch to FULL if you know that works best for you
          "deploy_policy": "PARTIAL"   # ALL_OR_NONE or VALIDATE are other options, depending on your needs
        }
        deploy_resp = ts.vcs_git_commits_deploy(request=deploy_req)
        print("Deployed to: " + org_name)
        print(json.dumps(deploy_resp, indent=2))