import os
import requests.exceptions
import json

from thoughtspot_rest_api_v1 import *

#
# Example of creating the setups of Orgs linked to Git branches in GitHub for dev->test->pre_prod->prod_per_customer
#

username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

org_names_to_create = [
    "dev",
    "test",
    "pre-prod",
    "cust_a",
    "cust_b"
]

org0: TSRestApiV2 = TSRestApiV2(server_url=server)
try:
    auth_token_response = org0.auth_token_full(username=username, password=password,
                                               validity_time_in_sec=3000, org_id=0)
    org0.bearer_token = auth_token_response['token']
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.content)
    exit()

names_org_id = {}

# Create the orgs
for name in org_names_to_create:
    resp = org0.orgs_create(name=name)
    names_org_id[name] = resp['id']

print("Created the following orgs: ")
print(json.dumps(names_org_id, indent=2))

# Config the Orgs with their Git branch
gh_repo_url = "https://github.com/yourCompany/repoName"
gh_username = "ghUsername"
gh_access_token = "ghAccessToken"  # Get this from GitHub
config_branch_name = "ts_config_branch"  # Whatever branch you create for this purpose

# This assumes the git branch name matches the org name, use additional mapping if necessary
# Create a connection to each org, so you can apply the config
for org_name in names_org_id:
    ts: TSRestApiV2 = TSRestApiV2(server_url=server)
    try:
        auth_resp = ts.auth_token_full(username=username, password=password,
                                       validity_time_in_sec=3000, org_id=names_org_id[org_name])
        ts.bearer_token = auth_resp['token']
    except requests.exceptions.HTTPError as e:
        print(e)
        print(e.response.content)
        exit()

    config_req = {
      "repository_url": gh_repo_url,
      "username": gh_username,
      "access_token": gh_access_token,
      "enable_guid_mapping": True,
      "branch_names": [
        org_name  # Use different mapping if branch names differ from org name
      ],
      "commit_branch_name": org_name,
      "configuration_branch_name": config_branch_name
    }
    config_resp = ts.vcs_git_config_create(request=config_req)
    print("Config response: ")
    print(json.dumps(config_resp, indent=2))

    # Initialize the mapping and commit files, which will be stored to the configuration branch
    commit_req = {
        "branch_name": org_name,
        "deploy_type": "FULL",
        "deploy_policy": "ALL_OR_NONE"
    }
    commit_resp = ts.vcs_git_commits_deploy(request=commit_req)
    print("Commit response: ")
    print(json.dumps(commit_resp, indent=2))
