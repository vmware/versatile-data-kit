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

Data engineers use one of the [IIngester](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L112) methods to send data for ingestion. The way data is ingested is controlled by different ingestion plugins which implement one of three possible methods (hooks)

* **pre_ingest_process** - called before data is about to be ingested
* **ingest_payload** - does the actual ingestion (sending the data to remote store)
* **post_ingest_process** - called after data is ingested (or failed to ingest in case of error)

[![vdk-ingest](https://github.com/vmware/versatile-data-kit/assets/2536458/a74582ef-eaaa-4693-91c4-41745212ad79)](https://www.plantuml.com/plantuml/uml/hPDFRzfC4CRl_XIZS843Yi8HnIWGb4DU3aYW5rMAP2tU0MzjppZxfnHL_UuTsm4KYvP3w-FCRsQUvrbuSbvP7yeYShcXIbbLWiFtW9GY_8X0lgcrV7ZcWYtC2fNcRJ7rR6TiDTfkQs5sk324DxfIs5iEf5lY2nO57nfaAOfCQYf5_igE3j1PiygFio9W5tjXybSjTEUdxq5Tkjsndr6awZhSpPLNyChREr0Evg_GQmQhoqMu-t_-7xn8ddXWcpTSNUcT57vYbqNO6uBl3mstVBY1ZLfiz6TiZiuRKjumjVpwmclHlrKEFvmiL8xt6sKnu-3m_etMcR5wM6yz0fAks91llIusqDjankEgv1oZICmF9usrCJX14zv-nTGdExQ9eJsw-dw_H9-nZlL5qY2AOvYw8wMPPPApq1VDs_DxWCyiAkq64CTHHEmH-1lQZqlF6QQv0pa2LUFMGSgqC_jWKOEXDtfyRAydbJeMh7HIMQmif-XSSlg5JoQHhAlrI-HZ428v3RLaVt06Hhy3_a9QcqgYSQT2uISJa9cs1hj0QHqJDFz9z6ZFIjPovBCtKI7LeJJbUSQmmYO-XFgL0KwzLjuqpOaF1UezbaZ-doJBpj-ALf0RsLubOlcY9_4Jok8N)

Details about ingestion hooks [can be seen here](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/plugin/plugin_input.py#L232).

You can see an example of [an ingest plugin here](https://github.com/vmware/versatile-data-kit/blob/main/examples/ingest-and-anonymize-plugin/plugins/vdk-poc-anonymize/src/vdk/plugin/anonymize/anonymization_plugin.py)

Ingestion hooks can be used for the following example use-cases (but not limited to them only):

* **Data Validation (pre_ingest_process):** Plugin validates incoming data against a predefined schema or rules. For example, it verifies if all necessary fields in sales data are present and correctly formatted.
* **Data Transformation (pre_ingest_process):** Plugin transforms the data into the required format. For instance, it might convert product names to uppercase or generate new fields in sales data, or anonymize PII data.
* **Data Ingestion (ingest_payload):** The Plugin Destination pushes data to the final storage, managing connections to systems like Amazon S3, Google Cloud Storage, or SQL databases.
* **Data Auditing (post_ingest_process):** In the post-ingest phase, the plugin serves as a data auditing tool, generating reports detailing data volume, errors, and timestamps of the ingestion process.
* **Metadata Update (post_ingest_process):** A plugin updates a metadata repository with information about the ingested data, like source, time, volume, schema.

## Public interfaces

Any backwards compatibility guarantees apply only to public interfaces.
Public interfaces are modules and packages defined or imported in vdk.api.*.
unless the documentation explicitly declares them to be provisional or internal interfaces.
Anything else is considered internal.
All public interfaces (classes or methods) must have documentation.
