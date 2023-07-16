# Plugins

Plugins make Versatile Data Kit adaptable to any organization's use-cases.
Example use-cases for plugins are different database connections, file systems, different transformation templates, or organization-specific best practices and patterns.


![VDK Plugin Components](../vdk-core/docs/vdk-components.svg)

## List of plugins

You can find a list of plugins that we have already developed in [plugins directory]().

## Installing and Using plugins

Installing a third-party plugin can be quickly done with pip:

```bash
pip install vdk-PLUGIN-NAME
```
Once the plugin is installed, vdk automatically finds it and activates it.

## Write your own plugin

### Quickstart

Install the latest Cookiecutter if you haven't installed it yet (this requires Cookiecutter 1.4.0 or higher):

```
pip install -U cookiecutter
```

Generate a VDK Plugin package project:

```
cookiecutter https://github.com/tozka/cookiecutter-vdk-plugin.git
```

Then

* Include your implementation files inside the `src` folder;
* Include any tests inside the `tests` so they can be ran by CI framework automatically.

### Explanation

A plugin is a python module that enhances or changes the behavior of Versatile Data Kit. <br>
A plugin is simply an implementation of one or more plugin hooks.

See all supported hook function specifications in [specs.py](../vdk-core/src/vdk/api/plugin/core_hook_spec.py).
The spec documentation contains details and examples for how a hook can be used.

To create a new plugin, there are only two steps necessary:<br>

* Create your implementation of the plugin's hook(s):
  You will need to mark it with the `hookimpl` decorator.
  Check out its [documentation here](../vdk-core/src/vdk/api/plugin/hook_markers.py) to see how you can configure the hook execution order
```python
# this is module myproject.pluginmodule, which will be our plugin
# define hookimpl as follows

# you need to have vdk-core as dependency
from vdk.api.plugin.hook_markers import hookimpl

# name of function must match name of hookspec function

@hookimpl(tryfirst=True)
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed with reasonable defaults.
    Other plugins will populate them. For example, there could be a plugin that reads env variables or parses config files.
    """
    config_builder.add(
        key="my_config",
        default_value="default-value-to-use-if-not-set-later",
        description="Description of my config.",
    )

# And here we can create another hook implementation
# let's use our configuration to print bar if it is set to foo everytime a job runs
@hookimpl
def run_job(self, context: JobContext):
    value = context.configuration.get_required_option('my_config')
    if value == "foo":
        print("bar")
```

* Register it as a plugin by listing the plugin modules in the vdk.plugin.run entry_point in your setup.py:
```python
entry_points={ 'vdk.plugin.run': ['name_of_plugin = myproject.pluginmodule'] }
```

<br>The plugin system is based on [pluggy.](https://pluggy.readthedocs.io/en/latest/index.html#implementations)

### Hook method names

As hook implementations can be functions (without class) it is recommended all hooks of the same family to share prefix. For example: db_connection_start, job_initialize.

## Types of plugins

### Generic Command-Line Lifecycle

![plugin cli life cycle](../vdk-core/docs/plugin-cli-lifecycle.svg)

Versatile Data Kit is used for executing different commands, some of them provided as plugins.
Using the above hooks, one can extend the functionality of any command by adding monitoring, customizing logging, or adding new options.

Check out the [CoreHookSpec class](../vdk-core/src/vdk/api/plugin/core_hook_spec.py) documentation for more details.

### Data Job Run (Execution) Cycle

![plugin data job run cycle](../vdk-core/docs/simple-data-job-lifecycle.svg)

The above image shows the normal run cycle of a data job. The hooks shown are only invoked when the "vdk run" command is invoked to execute a data job.


Check out the [JobRunSpecs class](../vdk-core/src/vdk/api/plugin/core_hook_spec.py) documentation for more details.

### Managed Database Connection Cycle

These are hook specifications that enable plugins to hook at PEP249 connection and cursor events during execution.
Sequence of evaluation:
1. db_connection_validate_operation
2. db_connection_decorate_operation
3. db_connection_execute_operation
 * in case of recovery needed -> db_connection_recover_operation

Check out the [connection hook spec](../vdk-core/src/vdk/api/plugin/connection_hook_spec.py) documentation for more details.

[![connection-hooks-activity-diagram](https://user-images.githubusercontent.com/2536458/228570184-4fba653c-dd6a-4a6d-80b3-bee83beb85e6.svg)](https://www.plantuml.com/plantuml/uml/ZPDFQnin4CNl-XG3kTY7-51wgGqb4BiKcaBwf-cXBKQMnbwrMib8sgI1_V0PQOMrcrs7-EBTVK-_DoEDhdpWBZIrPe8VWx86lbVAWrJyu7WDlh8FzCO3tt6FSBkvXJTltu4zekFHxU51XGhkrf_WsXg38Y4-MllFBnZJU40ZsKtwMx8M3WxHG7lYVCPGMGdThoN3JZT8-WGlwaJ9ICRQ7nvTorBv360f7FA084whLgmbJ1krduuVYJTMBevSOofgMUH5PipcP5pdrXDdu-b5Ar_rOwBm5KFZJEyhsDrVUbhbCli5DivRjpeVdlHnTexev0dyvZ-AXlZVljo0i7NDZNmUafOki3DIGjcWEwwLv07BmQQrMXsg48zaANVRqjpsFjkt9tka4MUDmhhNSsIqZpcb6Ug27r2-4fSxAxJnBcPmsI6rXnawPzqSGeK6Pe_ev-Iy_7NXKFwvV4_FUPlE1piKzXxTC7Z8Y3dPXdASbKweSwBs23DZep9ab4hYF715lbJwQiBfWpr6c95gpmfo69RKwJbpw1iTOjdSFAwOvZlKu9AsxRJUx7t082gGX8aB3AB4CyEtZqvhQFf-c_wdcbAUV-DQdxq6oO0oPVPlmRMjQnKWE6uyxsvYgUY52nzNZSF6j46MjhxSvwbkHNICi5cDMsmR9z3JaqOIvPXUXko5wgTJYcCoAGt85HhPrFe9)

### Data Ingestion Cycle

[![data-ingestion-workflow](https://github.com/vmware/versatile-data-kit/assets/2536458/8c27455c-9836-4110-8a8a-9660fba6706d)](https://www.plantuml.com/plantuml/uml/hPDFQzj04CNl-XH3V4aE9iH7avhOCO6cFXXiQWe1iTQEhArMCyh-gMjAltj7KXmJOUf3g-FCRsRVUxjwy46v42kR11Cimbm51PzfXpuO9jYmAtFB-oJnfQ5QELM1nzU8b27yIa2-gNEyVsJB3cPMPMLNp0Ax6JkDhjzQc1mNXl12Lmexnv5qHtn3Ap9QP2c2JMPgHU7CZXxGMxCg3pCRiOyzCOMp5lhpqzUeJjt-sEyaKKqThjeOdtbx1Sh3_1a6xM1zEX6kliw_m9FaYNl9kEMQok2ey0Exj75d27xUjTpoxW8swh3Htx5vSyUacdlk-FM9rw9_gpo-ELce4cytoc71qUFj2wqBu_ImsNe095speT1vNMnWi2bCm5N59IQ9c1zEMcjZy8AclFsEMKXpTgavlhFh2aF1-fC-IRf9Y0C2_q3tDlrOO5Pwa46eMmSUCgRSxA933OPUwFw-svZMwc1PwRHsM3lEqFlq-6edaqJMDPeanZ48aHw7ElBwvXqOdGV-ILhdDDMOgsZ3P08oqzKWZvGrrg7zpp2WUrUobaC-UXCLKXrAKo8Vmmf9GoWGcfi3EFOwUTEi9DvRr3kiaC9_IPPzk1Ij81UoFKiy8EbOsJy0)


## Public interfaces

Any backwards compatibility guarantees apply only to public interfaces.
Public interfaces are modules and packages defined or imported in vdk.api.*.
unless the documentation explicitly declares them to be provisional or internal interfaces.
Anything else is considered internal.
All public interfaces (classes or methods) must have documentation.
