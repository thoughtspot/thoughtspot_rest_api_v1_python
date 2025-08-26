import os
import requests.exceptions
import csv

from thoughtspot_rest_api_v1 import *


# Example functions for reporting of various counts of objects
# Useful for reporting various users / groups / domains / orgs for contractual compliance

#
server = os.getenv('server')        # or type in yourself

# Supply access token from REST API Playground or provide username/password securely
full_access_token = ""
username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself


ts: TSRestApiV2 = TSRestApiV2(server_url=server)
if full_access_token != "":
    ts.bearer_token = full_access_token
else:
    try:
        auth_token_response = ts.auth_token_full(username=username, password=password, validity_time_in_sec=3000)
        ts.bearer_token = auth_token_response['token']
    except requests.exceptions.HTTPError as e:
        print(e)
        print(e.response.content)
        exit()

#
# Main function to request every user
# Returns an Array with a simplified object of useful details
#
def all_users_details(org_id=0):
    print("\nRetrieving All Users Listing from /users/search endpoint")
    # record_size : -1 gets all listing
    search_request = {
        "record_size": -1,
        "record_offset": 0,
        "sort_options": {
            "field_name": "NAME",
            "order": "ASC"
        }
    }
    users = ts.users_search(request=search_request)
    users_table = []
    # print(json.dumps(users, indent=2))
    i = 0
    for user in users:

        # Grab all the essential details about a user, since the original object has so much
        guid = user["id"]
        name = user["name"]
        display_name = user["display_name"]

        email = user["email"]
        email_parts = email.split("@")
        email_domain = ""
        if len(email_parts) == 2:
            email_domain = email_parts[1]

        groups = user["user_groups"]
        orgs = user["orgs"]

        groups_count = len(groups)
        orgs_count = len(orgs)

        detail_row = {"id": guid,
                      "name": name,
                      "display_name": display_name,
                      "email": email,
                      "email_domain": email_domain,
                      "groups_count": groups_count,
                      "orgs_count": orgs_count,
                      "groups": groups,
                      "orgs": orgs
                      }
        users_table.append(detail_row)
    return users_table

def all_orgs_details():
    print("\nRetrieving All Orgs Listing from /orgs/search endpoint")
    # record_size : -1 gets all listing
    search_request = {}
    orgs = ts.orgs_search(request=search_request)
    # /orgs/search response is simple enough to simply use as is
    return orgs


def email_domains_csv(filename):
    user_details = all_users_details()

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['id', 'email_domain', 'groups_count', 'orgs_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for u in user_details:
            writer.writerow(u)

def email_domains_count_csv(filename):
    user_details = all_users_details()
    domains = {}
    for u in user_details:
        if u["email_domain"] not in domains:
            domains[u["email_domain"]] = 1
        else:
            domains[u["email_domain"]] += 1

    # print(json.dumps(domains, indent=2))

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['email_domain', 'users_count']

        writer = csv.writer(csvfile)
        # Write headers
        writer.writerow(fieldnames)
        for d in domains:
            writer.writerow([d, domains[d]])

def all_user_details_csv(filename, org_id=0, list_orgs=False, list_groups=False):
    user_details = all_users_details(org_id=0)

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['id', 'name', 'display_name', 'email', 'email_domain', 'groups_count', 'orgs_count']
        if list_orgs is True:
            fieldnames.append('orgs')
        if list_groups is True:
            fieldnames.append('groups')

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for u in user_details:
            writer.writerow(u)

def all_org_details_csv(filename):
    org_details = all_orgs_details()

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['id', 'name', 'status', 'description', 'visibility']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for o in org_details:
            writer.writerow(o)


email_domains_csv("user_domains_full.csv")
email_domains_count_csv("domains_count.csv")

# all_user_details_csv("users_export.csv", list_orgs=False, list_groups=False)

# all_org_details_csv("orgs.csv")

