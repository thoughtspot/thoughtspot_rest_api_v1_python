*A simple and pythonic Python implementation of ThoughtSpot's REST APIs (both V1 and V2).*

`thoughtspot_rest_api_v1` library implements the ThoughtSpot public REST APIs as directly as possible. It is not a "full SDK" with representation of each request and response type, but rather uses Python's Lists and Dicts for input and output.

Each API endpoint is represented by a single method within the `TSRestApiV1` or `TSRestApiV2` class.

Method and argument names closely match to the documented API endpoints, with a few minor changes are taken to make certain parameters more obvious for an end user, or to align with Pythonic conventions ('id' parameters in the API itself are written as 'guid' or '{object-name}_id' for example)

`TSRestApiV2` is implemented with an open `request` parameter for most endpoints, allowing you to construct any variation of a request based on what you build in the V2 REST API playground (a few simple endpoints have all their parameters implemented in the Python method).

`->` [Learning from the Source Code][jump-learning] </br>
`->` [Getting Started][jump-getting-started] </br>
`->` [Using `thoughtspot_rest_api_v1`][jump-tutorial] </br>
`->` [Additional Libraries][jump-libraries] </br>

---

## Learning from the source code
If you want to use the library as a reference for how a REST API endpoint is called correctly, look at the `/src/thoughtspot_rest_api_v1/tsrestapiv1.py` file. It contains the definition of all the ENUMs and the `TSRestApiV1` class. Similarly, the `TSRestApiV2` class is defined in the `/src/thoughtspot_rest_api_v1/tsrestapiv2.py` file.

The `TSRestApiV1` class uses the *requests* library to create an internal requests.Session object when the REST API sign-in command is run. This fulfils the ThoughtSpot REST API V1 requirement for session cookie details to be passed in every request.

Each method is implemented to be as self-contained as possible (other than using the shared session object), so you can use the library as an additional reference along with the V1 Playground (Swagger) to see exactly how any given call is implemented.

The library is designed to work with the latest version of ThoughtSpot Cloud. It should also work with Software versions 7.1.1 and later, but the library is not versioned, so please check your documentation for available endpoints within the release you use if on a Software release.

---

## Getting Started

To install thoughtspot_rest_api_v1, simply run this simple command in your terminal of choice:

```
$ python3 -m pip install thoughtspot_rest_api_v1
```

### Getting the source code

```
$ git clone https://github.com/thoughtspot/thoughtspot_rest_api_v1_python.git
```

Once you have a copy of the source, you can embed it in your own Python package, or install it into your site-packages easily:

```
$ cd thoughtspot_rest_api_v1_python
$ python3 -m pip install --upgrade
```

---

## Importing the library
    from thoughtspot_rest_api_v1 import *

This will bring the `TSRestApiV1` class, as well as the following enumerations:  `TSTypes`, `MetadataNames`, `MetadataSorts`, `MetadataSubtypes`, `MetadataCategories`, `ShareModes`, `Privileges`.

There is also a `TSRestApiV2` class, with enumerations: `TSTypesV2`, `ReportTypes`, to use the subset of REST API V2 capabilities that do not exist in the V1 API.

The `UserDetails`, `GroupsDetails` and `LiveboardDetails` classes are also imported automatically from `details_objects.py` to provide easy access to useful properties from the very complex responses from the `metadata/details` endpoint.

### Modifying the TSRestApiV1 requests.Session object (SSL errors, etc.)
The REST API commands are all handled via the `requests` module, using a `requests.Session` object. 

The session object used by all methods is accessible via:

    TSRestApiV1.requests_session

A common issue within organizations is SSL certificates not being available / included within the certificate store used by Python. One way around this issue is to use the `verify=False` argument in requests (this is not recommended, but may be the only easy path forward. Check with your security team and never use with ThoughtSpot Cloud or from outside your protected network).

This will set the Session object to `verify=False` for all calls:

    ts: TSRestApiV1 = TSRestApiV1(server_url=server)
    ts.requests_session.verify = False

If you find there are other options you need to set on the Session object for your particular situation, you can use the same technique to apply other changes.


## Logging into the REST API
You create a TSRestApiV1 object with the `server_url` argument, then use the `session_login()` method with username and password to log in. After login succeeds, the TSRestApiV1 object has an open requests.Session object which maintains the necessary cookies to use the REST API continuously .


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

- `TSTypes`: Combines MetadataNames and MetadataSubtypes into a single set of unique values, so that you don't need to worry about when to use Subtypes. The implementations of the /metadata/ endpoints read the values from this ENUM and issue the correct REST API command
- `MetadataCategories`: Contains the options for the argument called 'category' in metadata calls
- `MetadataSorts`: Contains the available sort options for the argument called 'sort' in metadata calls
- `ShareModes`: The modes used in the JSON of the /security/share endpoint
- `Privileges`: The name of the Privileges that Groups can have (and users can inherit) in ThoughtSpot
- `MetadataTypes`: The namings used in the 'type' parameter of the /metadata/ endpoint calls, with simplified names that matches the names in the UI and standard ThoughtSpot documentation. For example, MetadataTypes.GROUP = 'USER_GROUP'
- `MetadataSubtypes`: The available options for the 'subtype' argument used for certain metadata calls

## Logging into REST API V2
REST API V2 allows for Bearer Token authentication, which is the preferred method rather than session cookie sign-in. You create a TSRestApiV2 object with the `server_url` argument.
Next request a Full Access token using `auth_token_full()`. Get the `token` value from the response, then set the `bearer_token` property of the TSRestApiV2 object with the token. The object will keep the bearer token and use it in the headers of any subsequent call.

    
    from thoughtspot_rest_api_v1 import *

    username = os.getenv('username')  # or type in yourself
    password = os.getenv('password')  # or type in yourself
    server = os.getenv('server')      # or type in yourself

    ts: TSRestApiV2 = TSRestApiV2(server_url=server)
    try:
        auth_token_response = ts.auth_token_full(username=username, password=password, validity_time_in_sec=3000)
    except requests.exceptions.HTTPError as e:
        print(e)
        print(e.response.content)
    ts.bearer_token = auth_token_response['token']

### V2 Methods
REST API V2 exclusively uses JSON for the request format. Because Python Dicts map nearly directly to JSON, many of the methods for endpoints simply have a 'request=' argument, with the expectation that you form the request per the Documentation / Playground however you see fit:
    
    search_request = {'org_identifiers': ['My Org']}
    users_response = ts.users_search(request=search_request)

Other methods, where the potential request arguments are very small / simple, do have the full set of arguments represented in the Python method:
    
    users_reset_password(user_identifier='bill.guy@company.com', new_password='agreatnewpassword')

### Implementing new V2 methods
The TSRestApiV2 class includes three 'base' methods, one for each HTTP request verb one might make to the V2.0 REST API:

    TSRestApiV2.get_request(endpoint)
    TSRestApiV2.post_request(endpoint, request=None)
    TSRestApiV2.post_request_binary(endpoint, request=None)  # for binary responses

The `endpoint` argument only takes the unique part of the endpoint, like `users/create`, not the entire URL. 

All of the methods for particular endpoints call these base methods like:

    def users_update(self, user_identifier: str, request: Dict):
        endpoint = 'users/{}/update'.format(user_identifier)
        return self.post_request(endpoint=endpoint, request=request)

If a method is not implemented in the library (a new version has rolled out before a maintainer has added the new endpoint to the library), you can simply implement it "externally" using these 'base methods'.

You can also reference the `TSRestApiV2.requests_session` object directly if you want to issue something directly using the Python `requests` library.

### V2 Examples
The /examples_v2/ directory of this repository contains examples of using the V2 API, often as a parallel to a script with the same name in the V1 /examples/ directory.

## TML operations
One primary use case of the REST APIs is to import and export ThoughtSpot Modeling Language (TML) files.

### Disabling FQN export
ThoughtSpot 8.9 adds the 'export_fqn' option to the `/metadata/tml/export` endpoint, which includes the GUID references to all related objects in an exported TML file. Because this is very useful, the library defaults to including the argument set to true in all TML Export methods.

Older versions of ThoughtSpot will not support this option, so there is a global `can_export_fqn` flag to disable it. Set it to False if you are encountering errors and are on a version prior to 8.9:
    
    ts: TSRestApiV1 = TSRestApiV1(server_url=server)
    ts.can_export_fqn = False

### Retrieving the TML as a Python OrderedDict from REST API
If you want to use the TML classes to programmatically adjust the returned TML, there is a `export_tml(guid)` method which retrieves the TML from the API in JSON format and then returns it as a Python OrderedDict.

This method is designed to be the input of the `thoughtspot_tml` library

    lb_tml = ts.metadata_tml_export(guid=lb_guid, export_associated=False)


### Downloading the TML directly as string
If you want the TML as you would see it within the TML editor, use

`ts.metadata_tml_export_string(guid, formattype, export_associated=False)`

formattype defaults to 'YAML' but can be set to 'JSON'.

This method returns a Python str object, which can then be editing in memory or saved directly to disk. 

### Download TML with Name-GUID map from export_associated=true
TML files don't include the GUIDs of associated objects, but they are available in the headers of the response when `export_associated` is set to `true`.

There are two functions that export both the TML and a Dict of structure `{'object_name' : 'guid' }`, which can be used to add the `FQN` property to the TML.

    tml_od, name_guid_map = ts.metadata_tml_export_with_associations_map(guid=lb_guid)
    tml_str, name_guid_map = ts.metadata_tml_export_string_with_associations_map(guid=lb_guid)

To add the `FQN` properties from the dict mapping, you'll need to modify the TML as an object, so the export_string method is less useful than the version that exports the OrderedDict.

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

---

## Metadata operations
Doing any actions with the REST APIs requires knowing the GUIDs of the objects. The `/metadata/` endpoints are incredibly flexible, allowing you to retrieve details about almost any object type from the same endpoints. This flexibility means you must set a number of arguments with each call, including using the internal names of the object types.

### TSTypes, MetadataTypes and MetadataSubtypes and other ENUMs
Because the internal API identifiers of the object types in V1 often do not reflect the names used in the current versions of ThoughtSpot, there are ENUMs provided within the library to map the 'product name' to the REST API string value: `TSTypes`, `MetadataTypes`, and `MetadataSubtypes`. 

The REST API has a single object_type for Tables, Views, and Worksheets, and uses an additional 'sub_type' property if you need to distinguish between those objects. 

Because of the complexity of remembering to add the sub-type, the `TSTypes` ENUM should be used - it uses the sub-types of the data objects rather than the type. The implementation of all of the `metadata` endpoints works even if a sub-type is passed into the `object_type` argument. 

This allows you to do:

    objs = ts.metadata_listobjectheaders(object_type=TSTypes.WORKSHEET, sort='MODIFIED', sort_ascending=False, category=category_filter, fetchids=object_guid_list)

whereas otherwise you would need to specify both type and sub-type for a Worksheet or other data object

    objs = ts.metadata_listobjectheaders(object_type=MetadataTypes.WORKSHEET, subtypes=[MetadataSubtypes.WORKSHEET], sort='MODIFIED', sort_ascending=False, category=category_filter, fetchids=object_guid_list)

Other ENUMs include: `Sorts`, `Categories`, `ShareModes`, `Privileges`, `PermissionTypes`, and `GroupVisibility`. Often the keys for these enums is no different than the string values themselves, but they provide easy access to the full set of values when using auto-complete in your IDE.

### metadata_listobjectheaders and metadata_list
The `metadata/listobjectheaders` and `metadata/list` REST API endpoints do relatively the same thing, although there are slight differences in the responses from each call.

The implementation is exactly as described in the documentation (https://developers.thoughtspot.com/docs/?pageid=metadata-api#object-header) with these changes for ease of use and clarity:

 - 'object_type' argument will accept the sub_types for the data object types and automatically structure the REST API request appropriately
 - 'filter' argument is the name given to the 'pattern' argument in the REST API command, as the name pattern seemed unclear to users

`metadata/list` returns a slightly more complex object than `metadata/listobjectheaders`. To get the same list of objects from `metadata/list`, use the `headers` key from the response:

    objs = ts.metadata_listobjectheaders(object_type=TSTypes.WORKSHEET, sort='MODIFIED', sort_ascending=False)

    for obj in objs:
        # parse the objects

vs. 

    response = ts.metadata_list(object_type=TSTypes.WORKSHEET, sort='MODIFIED', sort_ascending=False)
    objs = response['headers']
    for obj in objs:
        # parse the objects

### metadata_details and Details classes
`metadata_details` returns the full internal object model of a given object, which is typically a very large and complex response to parse.

The Details classes defined in `details_objects.py` can wrap around the response with easy methods to retrieve useful properties from this response.

How to use:

    details_response = ts.metadata_details(object_type=TSTypes.GROUP, object_guids=['{guid}'])
    group_details = GroupDetails(details_obj=details_response[0])
    privs = group_details.privileges()
    
    details_response = ts.metadata_details(object_type=TSTypes.USER, object_guids=['{guid}'])
    user_details = UserDetails(details_obj=details_response[0])
    user_created = user_details.created_timestamp()
    user_inherited_groups = user_details.inherited_groups()

Some of the properties that were previously only accessible from the `metadata/details` response may be available from endpoints in the V2 REST API, so it is worth checking there first before working with the details responses.
 

### Connection details 
Connections, representing basic connection details of the external data sources ThoughtSpot connects to, have their own set of endpoints in `/connection/` outside of the `/metadata/` endpoints. 

There are few of these endpoints used by ThoughtSpot's UI but not currently ported and documented to the `/v1/public/` endpoints that have been implemented as part of this library to help bridge customers until public endpoints with the details have been made available.

### Dependent Objects API calls


## User and Group operations
The `/user/` and `/group/` endpoints contain CRUD operation endpoints for these two object types (while other objects are created via TML import and export). They allow you to sync users and groups to other systems.

Following REST API principles, many of the endpoints themselves are the same but use different HTTP verbs to achieve different actions. The TSRestApiV1 methods distinguish these following the naming pattern of {fixed_endpoint_separated_by_underscores}_{http_verb} i.e. `POST /group/{groupid}/users` becomes `group_users_post()` while the PUT version of the same endpoint becomes `group_users_put()`

### Metadata operations
`GET /group/` and `GET /user/` are equivalent to using `metadata/listobjectheaders`, they are just convenience methods to get the same exact result, with ability to filter directly by name. However, there are additional endpoints that provide more specific information that is difficult to determine otherwise.

`GET /group/listuser/{groupid}`, `GET /group/{groupid}/users/` , `GET /group/{groupid}/groups`, and `GET /user/{userid}/groups` each give a specific insight into the relationship between groups and users, starting from an individual group or user's perspective. They can save a huge amount of time when auditing how your system is configured or why certain privileges / access control is working in a particular way.

For example, if you want to know the set of users assigned to a group, you would do:

    group_name = 'Group A'
    group = ts.group_get(name=group_name)
    group_guid = group['header']['id']
    users_in_group = ts.group_users_get(group_guid=group_guid)
    for user in users_in_group:
        # do something with user headers

### CRUD operations
As much as possible, the parameters within the endpoints or as part of the POST/PUT bodies have been mapped directly to methods with arguments matching the definitions in the documentation. Differences may occur such as using `guid` in place of `id` per Python's spec, or making arguments plural or singular when the API argument is named the opposite way.

The response is always the full JSON response from the API unless the API does not return a JSON response. You will need to parse the response to get essential details (such as the new GUID assigned to the newly created object)

Example:

    new_group = ts.group_post(group_name='group_1', display_name='Group 1', privileges=[Privileges.CAN_DOWNLOAD_DATA, Privileges.HAS_SPOTIQ_PRIVILEGE])
    new_group_guid = new_group['headers']['id']

## Sharing / object access : /security/ endpoints
Object access in ThoughtSpot is controlled by Sharing. Objects are owned by their `author` (this is different from any `owner` property you might see in API responses) and can only be accessed by others if they are shared.

### Sharing an object
The `/security/share` endpoint is used to share objects with users and groups, which becomes `security_share()` of the `TSRestApiV11` class. 

You can specify if the user or group has READ_ONLY or EDIT access through the `permissions=` argument, but it is relatively complex object format. For that reason, the library provides the `create_shared_permissions()` helper method to get the object with the right format to send into the permissions= argument:

    perms = ts.create_share_permissions(read_only_users_or_groups_guids=read_only_guids, 
                                        edit_access_users_or_groups_guids=edit_guids)
    ts.security_share(shared_object_type=TSTypes.LIVEBOARD, shared_object_guids=[lb_guid], permissions=perms)

You can also remove sharing from an object, using the third optional argument of `create_share_permissions(remove_access_users_or_groups=)`:

    guids_to_remove_sharing_from = ['{groupGuid6}', '{groupGuid7}']
    remove_perms = ts.create_share_permissions(remove_access_users_or_groups_groups=guids_to_remove_sharing_from)
    ts.security_share(shared_object_type=TSTypes.LIVEBOARD, shared_object_guids=[lb_guid],
                      permissions=remove_perms)

You can share an individual viz from a Liveboard rather than the whole Liveboard using `security_shareviz()`. There is not multiple levels of permissions on a shared viz:

    viz_guid = '{vizGuid}'
    ts.security_shareviz(shared_object_type=TSTypes.LIVEBOARD, pinboard_guid=lb_guid, viz_guid=viz_guid, 
                         principal_ids=read_only_guids)

### Auditing permissions on an object
The set of sharing set on an object is referred to as permissions. There are several similar endpoints in the V1 REST API for determining permissions: `security_metadata_permissions()`, `security_metadata_permissions_by_id()` and `security_effectivepermissionbulk()`. 

Please see the REST API documentation to understand the main differences, but in essence `security_metadata_permissions()` can retrieve multiple objects of the same type, while `security_metadata_permissions_by_id()` only brings back one object at a time. Both have a `permission_type=` argument that can take the values in the `PermissionTypes` ENUM, either `EFFECTIVE` or `DEFINED`

    ts.security_metadata_permissions_by_id(object_type=TSTypes.LIVEBOARD, object_guid=lb_guid, dependent_share=False,
                                           permission_type=PermissionTypes.EFFECTIVE)

  
`security_effectivepermissionbulk()` allows you to specify objects of multiple types using a more complex Dict for the `ids_by_type=` argument, but it does not let you choose between the PermissionTypes the way the other endpoints do:

    ts.security_effectivepermissionbulk(ids_by_type={MetadataTypes.LIVEBOARD: ['{lbGuid1}'], 
                                                     MetadataTypes.ANSWER: ['{aGuid1}']}
                                        )

These endpoints have been simplified in REST API V2 into `security_permission_tsobject()` to get the set of users and groups who can see/edit the object, and `ts_security_permission_principal()` to see what content of a given type the user or group has access to:

    ts2.security_permission_principal(username_or_group_name='auser@domain.com')  # alternatively username_or_group_guid=
    ts2.security_permission_tsobject(guid=lb_guid, object_type=TSTypesV2.LIVEBOARD, include_dependents=False)

## /session/ endpoints
The `/session/` REST API endpoints are mixed between those intended to be used from the end user's browser (like `/session/login/token`) and others used in back-end processes to help facilitate SSO and session management. 

In general, anything intended as part of the Trusted Authentication workflow from the browser should be handled by the Visual Embed SDK, and once that session is established, other methods like `POST /session/homepinboard` or `POST /session/logout` can be sent from the browser to achieve integration with the embedding application.


### Trusted authentication token requests
The method `ts.session_auth_token()` is used to request the login token for a trusted auth flow. This should only be used by a back-end service, with the `secret_key` from the ThoughtSpot instance stored and accessed via a secure method (up to you how best to do this). You also must develop the process to securely determine the username of the user logged into the embedding application (see https://developers.thoughtspot.com/docs/?pageid=trusted-auth for full documentation):
    
    user_from_request = get_username_from_secure_request(request)
    token = ts.session_auth_token(secret_key=securely_accessed_secret_key, username=user_from_request)

The example script `examples/trusted_authentication_with_authorization.py` shows how to combine various metadata and CRUD operations with the request for the trusted authorization login token. 

## Data and export APIs
In the V1 REST API, the Liveboard PDF Export endpoint lives under `/export/` while the Liveboard Data and Search Data endpoints which export data in JSON format live in the top level. In V2, the Data endpoints live under the `/data/` higher level endpoint. 

Thus the methods are `ts.pinboarddata()` and `ts.searchdata()` on the `TSRestApiV1` class, while the equivalent in V2 for saved Answers is `data_answer_data()`. 

These same features have been relocated in the V2 REST API under `/report/` and `/data/` endpoints.

    try:
        liveboard_pdf = ts.export_pinboard_pdf(pinboard_id=first_liveboard_id, footer_text="Viz by the foot",
                                               cover_page=False, filter_page=False, landscape_or_portrait='PORTRAIT')
        new_file_name = "../Test PDF.pdf"
        with open(new_file_name, 'bw') as fh:
            fh.write(liveboard_pdf)
    except requests.exceptions.HTTPError as e:
        print(e)

`examples/liveboard_pdf_export.py` shows how to use to get binary object exports and save them to disk, although you could do further processing of those objects in memory. 

The Data APIs return back the data from a saved object or an arbitrary TML search string in a JSON format. Please see `examples/data_exports.py` for the various options and how to work with the result sets.

    lb_guid = '{lbGuid}'
    viz_on_lb_guid = '{vizGuid}'  # For retrieving from one specific viz

    lb_data_response = ts.pinboarddata(pinboard_guid=lb_guid)

    viz_data_response = ts.pinboarddata(pinboard_guid=lb_guid, vizids=[viz_on_lb_guid])


## Additional libraries
`thoughtspot_tml` is a library for processing the ThoughtSpot Modeling Language (TML) files. You can use `thoughtspot_tml` to manipulate TML files from disk or exported via the REST API.

`cs_tools` is a package of command-line tools built by the ThoughtSpot Professional Services team, aimed at ThoughtSpot administrators. 


[jump-learning]: <#learning-from-the-source-code> "jump: Learning"
[jump-getting-started]: <#getting-started> "jump: Getting Started"
[jump-tutorial]: <#importing-the-library> "jump: Intro Tutorial"
[jump-libraries]: <#additional-libraries> "jump: More Libraries"
