# thoughtspot_rest_api_v1_python
Simple Python implementation of V1 REST API

## Introduction
thoughtspot_rest_api_v1 implements the ThoughtSpot V1 REST API as directly as possible. Each API endpoint is represented by a single method within the TSRestApiV1 class. The names of the methods and their arguments match up to the documented API endpoints as much as is practical, with a few minor changes to make certain argument names more obvious for an end user.

The TSRestApiV1 class uses the *requests* library to create an internal requests.Session object when the REST API sign-in command is run. This fulfils the ThoughtSpot REST API V1 requirement for session cookie details to be passed in every request.

Each method is implemented to be as self-contained as possible (other than using the shared session object), so you can use the library as an additional reference along with the V1 Playground (Swagger) to see exactly how any given call is implemented.

The library is designed to work with the latest version of ThoughtSpot Cloud. It should also work with Software versions 7.1.1 and later, but the library is not versioned, so please check your documentation for available endpoints within the release you use if on a Software release.

### Additional libraries
`thoughtspot_tml` is a library for processing the ThoughtSpot Modeling Language (TML) files. You can use `thoughtspot_tml` to manipulate TML files from disk or exported via the REST API.

`ts_rest_api_and_tml_tools` is a convenience library that imports both `thoughtspot_rest_api_v1` and `thoughtspot_tml` and wraps them in more convenient and obvious packaging. It also contains many example scripts to do common workflows. In particular, there are many examples of SDLC use cases that involve REST API commands and TML manipulation.

`cs_tools` is a package of command-line tools built by the ThoughtSpot professional services team, aimed at ThoughtSpot administrators. 

### Learning from the source code
If you want to use the library as a reference for how a REST API endpoint is called correctly, look at the `/src/thoughtspot_rest_api_v1/tsrestapiv1.py` file. It contains the definition of all the ENUMs and the TSRestApiV1 class.

## Importing the library
    from thoughtspot_rest_api_v1 import *

This will bring the `TSRestApiV1` class, as well as the following enumerations:  `MetadataNames`, `MetadataSorts`, `MetadataSubtypes`, `MetadataCategories`, `ShareModes`, `Privileges`.

## Logging into the REST API
You create a TSRestApiV1 object with the `server_url` argument, then use the `session_login()` method with username and password to log in. After login succeeds, the TSRestApiV1 object has an open requests. Session object which maintains the necessary cookies to use the REST API continuously .


    username = os.getenv('username')  # or type in yourself
    password = os.getenv('password')  # or type in yourself
    server = os.getenv('server')      # or type in yourself

    ts: TSRestApiV1 = TSRestApiV1(server_url=server)
    try:
        ts.session_login(username=username, password=password)
    except requests.exceptions.HTTPError as e:
        print(e)
        print(e.response.content)

In all further examples, the `ts` variable represents a `TSRestApiV1` object after the `session_login()` method has been called successfully.

## Logging out of the REST API
The `session_logout()` method of the ThoughtSpot class will send the API request to end your TS session. After you do this, you may want to del the ThoughtSpot object if you are doing a lot of other work to end the request.Session object:
    
    ts.session_logout()
    del ts

## ENUM data structures
The ThoughtSpot API has internal namings for many features, which require looking up in the reference guide. To help out, the tsrestapiv1.py file defines several ENUM style classes:

- MetadataNames: The namings used in the 'type' parameter of the /metadata/ endpoint calls, with simplified names that matches the names in the UI and standard ThoughtSpot documentation. For example, MetadataNames.GROUP = 'USER_GROUP'
- MetadataSubtypes: The available options for the 'subtype' argument used for certain metadata calls
- MetadataCategories: Contains the options for the argument called 'category' in metadata calls
- MetadataSorts: Contains the available sort options for the argument called 'sort' in metadata calls
- ShareModes: The modes used in the JSON of the /security/share endpoint
- Privileges: The name of the Privileges that Groups can have (and users can inherit) in ThoughtSpot

## TML operations
One primary use case of the 

### Retrieving the TML as a Python OrderedDict from REST API
If you want to use the TML classes to programmatically adjust the returned TML, there is a `export_tml(guid)` method which retrieves the TML from the API in JSON format and then returns it as a Python OrderedDict.

This method is designed to be the input of the `thoughtspot_tml` library

    lb_tml = ts.metadata_tml_export(guid=lb_guid, export_associated=False)


### Downloading the TML directly as string
If you want the TML as you would see it within the TML editor, use

`ts.metadata_tml_export_string(guid, formattype, export_associated=False)`

formattype defaults to 'YAML' but can be set to 'JSON'.

This method returns a Python str object, which can then be editing in memory or saved directly to disk. 


### Importing/Publishing TML back to ThoughtSpot Server
Similar to `metadata_tml_export()`, `metadata_tml_import()` uses a Python OrderedDict as input (or a List containing OrderedDict objects for multiple import). The method converts the OrderedDict to JSON format internally for use in the REST API request body.

    ts.metadata_tml_import(tml_ordereddict, create_new_on_server=False, validate_only=False))

You can also import multiple using a List:
    
    ts.metadata_tml_import([tml_od_1, tml_od_2], create_new_on_server=True)

There are a few optional arguments: 
- `create_new_on_server` - you must set this to True, otherwise it will update the existing object with the same GUID.
- `validate_only` - If set to True, this only runs through validation and returns the response with any errors listed'

There is a static method for pulling the GUIDs from the import command response `ts.guids_from_imported_tml()`, which returns the GUIDs in a list in the order they were sent to the import.

The following example uses the `thoughtspot_tml` library, where each object has a `.tml` property containing the OrderedDict:

    # Get create Worksheet object
    ws_obj = Worksheet(ts.metaddata_export_tml(guid=lb_guid))
    # Send the .tml property, not the whole object
    import_response = ts.metadata_import_tml(ws_obj.tml, create_new_on_server=False)
    new_guids = ts.guids_from_imported_tml(import_response)
    new_guid = new_guids[0]  # when only a single TML imported


