# Versatile Data Kit Control CLI

VDK Control CLI is meant for Data Engineers to use to manage the lifecycle of jobs - create, delete, deploy, configure Data Jobs.

To build or contribute, see [CONTRIBUTING.md](./CONTRIBUTING.md).

## Installation
Install VDK Control CLI with:
```bash
pip install vdk-control-cli
```
This will install console application called `vdkcli`

Then run help to see what it can do:
```bash
vdkcli --help
```

`vdkcli` is the name of the console application only when vdk-control-cli is installed autonomously. Typically,
it is a dependency of Versatile Data Kit and the console application is `vdk` (hence, all commands in error and help
messages in this project refer to `vdk`). Keep in mind that if you are using this project autonomously, you should
use `vdkcli` command instead of `vdk`.

### Environment variables:

* VDK_AUTHENTICATION_DISABLE  - disables security (vdk login will not be required). See Security section.
* VDK_BASE_CONFIG_FOLDER -  Override local base configuration folder (by default $HOME folder) . Use in case multiple users need to login (e.g in case of automation) on same machine.

### Security
By default, all operation require authentication: vdk login must have finished successfully.
You can disable it with environment variable `VDK_AUTHENTICATION_DISABLE=true`
This would only work if Control Service which VDK CLI uses also has security disabled.

In case of credentials type login flow we start a process on port `31113` to receive the credentials.
If you already have process running on `31113` you can override the value.
To override the port set environmental variable `OAUTH_PORT` with free port which the client can use.

## Plugins

### Installing and Using plugins

Installing a third party plugin can be easily done with pip:

```bash
pip install vdk-control-cli-NAME
pip uninstall vdk-control-cli-NAME
```
If a plugin is installed, vdk automatically finds and integrates it.

### Write your own plugin

A plugin is python module that enhances or changes the behaviour of the vdk cli. <br>
A plugin contains one or multiple hook functions.

See all supported hook function specifications that can be implemented in [specs.py](src/taurus/vdk/api/plugin/specs.py)

In order to create a new plugin there are only 2 steps:<br>

* Create your implementation of the plugin's hook(s):
```python
# define hookimpl as follows (library requirement: pluggy)
hookimpl = pluggy.HookimplMarker("vdk_control_cli.plugin")
# though it's better to use `taurus.vdk.plugin.markers.hookimpl` from vdk-control-cli python package

# name of function must match name of hookspec function
@hookimpl
def get_default_commands_options():
    # your implementation here ; for example to set defaults for `vdk login --type --oauth2-authorization-url` command
    default_options = {
        "login": {
            "auth_type": "api-token", # note values must be valid or the plugin may break the CLI, no checking is done at this point
            "api_token_authorization_url": "http://localhost/authorize" # replace dashes with underscore for the argument name
        }
    }
    return default_options
```
* Register as plugin by listing the plugin modules in vdk_control_cli.plugin entry_point in your setup.py:
```python
    entry_points={ 'vdk_control_cli.plugin': ['name_of_plugin = myproject.pluginmodule'] }
```

<br>The plugin system is based on [pluggy.](https://pluggy.readthedocs.io/en/latest/index.html#implementations)
<br>SDK Extensibility design can be seen [here](https://github.com/vmware/versatile-data-kit/tree/main/specs)

## Authentication

In order to use credentials login type you need to create OAuth2 Application.
