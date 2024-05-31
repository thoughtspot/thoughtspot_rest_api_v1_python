# Based on https://github.com/psf/requests/issues/2011#issuecomment-477784399
# By default Requests library does not have a set timeout.
# This patches in the timeout into all calls used by TSRestApiV2 object
# Same principal lets you modify with anything else from the requests library documentation

import os
import requests.exceptions
import functools

from thoughtspot_rest_api_v1 import *


# Details about objects within ThoughtSpot all are accessed through 'metadata/' endpoints, which can be used
# for almost every object type


username = os.getenv('username')  # or type in yourself
password = os.getenv('password')  # or type in yourself
server = os.getenv('server')        # or type in yourself

ts: TSRestApiV2 = TSRestApiV2(server_url=server)

timeout_in_secs = 300

session = ts.requests_session
for method in ('get', 'options', 'head', 'post', 'put', 'patch', 'delete'):
    setattr(session, method, functools.partial(getattr(session, method), timeout=timeout_in_secs))

# Add TCP keepalive
ts.set_tcp_keep_alive_adaptor(ts.get_default_tcp_keep_alive_adaptor())

# Now any call you make will send the specified timeout along to Requests

#  ts.session_login() ... etc