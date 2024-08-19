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


def create_orgs(org_names):
    # Create the orgs
    orgs_name_id_map = {}
    for name in org_names_to_create:
        resp = org0.orgs_create(name=name)
        orgs_name_id_map[name] = resp['id']

    print("Created the following orgs: ")
    print(json.dumps(orgs_name_id_map, indent=2))
    return orgs_name_id_map


def get_orgs_names_ids_map():
    resp = org0.orgs_search(request={"visibility": "SHOW", "status": "ACTIVE"})
    orgs_name_id_map = {}
    for i in resp:
        if i["name"] in org_names_to_create:
            orgs_name_id_map[i["name"]] = i["id"]
    return orgs_name_id_map


# If the orgs already exist, comment this out and get a { org_name : org_id } map from /orgs/search endpoint with below
names_org_id = create_orgs(org_names_to_create)
# names_org_id = get_orgs_names_ids_map()

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

    # If you need to clear a previous config, delete with:
    # delete_config_resp = ts.vcs_git_config_create(request={})
    # print("Delete Config response: ")
    # print(json.dumps(delete_config_resp, indent=2))

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

    # Once you've initialized the mapping file, go to your Config Branch in GitHub
    # You will see two directories, one that ends in `.mapping`
    # Inside this directory, will be an org-{org_id}.json file
    # Per https://developers.thoughtspot.com/docs/guid-mapping#_using_mapping_for_table_tml_properties
    # You can manually edit the file and add entries
    # to swap out the db:, schema: and even db_table: properties
    # When you actually deploy any objects using the /vcs/git/commits/deploy endpoint,
    # these mappings will be in use, and ThoughtSpot will update the .mapping file with mappings of deployed objects
    # See git_deploy_commits_to_prod_single_tenants.py for script using the vcs_git_commits_deploy() method
