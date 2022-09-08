# REST API example scripts

## objects_info_metadata.py
Basic example showing many ways to use the REST API library for querying. Start here to learn the syntax and capabilities

## liveboard_pdf_export.py
Simple example of programmatically exporting a PDF of a Liveboard

## delete_object.py
A usage of the V2 REST API for its object deletion endpoint

## tag_objects.py
Short example of how to find tags and assign them to objects. V2 has APIs for tag CRUD but they are not shown yet in this example

## transfer_object_ownership.py
Transferring content ownership is only achieved via API, but can be very useful.

## audit_object_access.py
Set of examples using the TS Cloud REST APIs to retrieve sharing permissions on various objects.

Combines several different metadata commands to get all the human-readable names necessary for a person to audit the sharing capabilities.

# Not ported yet

### import_tables_rest_api_example.py
Advanced script for using the REST API to bring in all tables from a given schema, rather than having to select them all via the UI. 

You may instead want to generate TML for the Table objects, then import the TML (gives more control over options). See tml_and_sdlc/tml_from_scratch.py for code to perform that action.

Currently has only been tested on Snowflake connections.