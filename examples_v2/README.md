# Examples scripts using V2.0 ThoughtSpot REST API

# Orgs and SDLC

## create_orgs_with_linked_git_branch.py
Create dev-test-prod Orgs with matching Git branches for basic SDLC setup in ThoughtSpot

## create_connection_on_orgs.py
Create matching connection objects across Orgs, with whatever desired variations are necessary, so that Git REST API deploy of Tables + other objects will work

## git_deploy_commits_to_prod_single_tenants.py
In single-tenant database pattern, there is a prod org per end customer. Script shows cycling through each of those Orgs and deploying commits from a single pre-prod/release branch, or 

## org_migration_users_groups.py
When you convert a cluster to Orgs, all content remains on the Primary org. This first script allows you to determine which users to add to which Orgs, and recreates Groups on those Orgs to add the users to

## org_migration_data_content.py
When you convert a cluster to Orgs, all content remains on the Primary org. This second script copies content from one Org to another, and reshares to the same Groups / Users as was set up in the Primary org

# Users, Groups, Access Control

## share_objects_access_control.py
Sample of sharing (access control) programmatically, to use after content is created

## abac_token_parameters.py
Example of configuring a Full Access Token with the newer ABAC / user_parameters section

## transfer_object_ownership.py

## tag_objects.py
  
 
