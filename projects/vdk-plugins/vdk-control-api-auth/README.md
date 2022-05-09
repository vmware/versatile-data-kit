# vdk-control-api-auth

vdk-control-api-auth is a plugin library that implements authentication
utilities used by vdk-control-cli and other plugins.

## Usage

This is a library plugin, not a runnable plugin, and it is intended to be
used as a dependency for other plugins, which need to authenticate users.

To use the library within a plugin or another Versatile Data Kit component,
just import the `Authentication` class, and create an instance of it. The
different authentication flows require different parameters to be specified.

Once everything is done, in order to authenticate, call `.authenticate()` on
the `Authentication` instance.

Example Usage:
```python
from vdk.plugin.control_api_auth.authentication import Authentication

auth = Authentication(
    token="<oauth-api-token>",
    authorization_url="https://some-authorization-endpoint",
    auth_type="api-token",
)

auth.authenticate()   # authenticate

auth.read_access_token()   # fetch the cached access token
```

## Build and testing

In order to build and test a plugin go to the plugin directory and use `../build-plugin.sh` script to build it
