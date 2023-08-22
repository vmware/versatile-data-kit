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