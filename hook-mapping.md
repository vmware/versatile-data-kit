Overall: 

we can manipulate the order of most off the hooks in vdk-core even if we do not use tryfirst/trylast 
-> discourage using especially trylast in core

only the hook which are essential should be marked tryfirst in core 
-> example creation of job_context

all the other core-hooks should be standard and their creation should be ordered so we know how they are executed / or all the core-hooks should be tryfirst
-> https://github.com/vmware/versatile-data-kit/blob/a45ee03578188b0445a823fdfe80a8a41f102ecf/projects/vdk-core/src/vdk/internal/builtin_plugins/builtin_hook_impl.py#L115
-> this one is mostly applicable for hooks inside a plugin like vdk_initialize, initialize_job, vdk_configure , run_step , etc.

~~ looking aat https://github.com/vmware/versatile-data-kit/blob/a45ee03578188b0445a823fdfe80a8a41f102ecf/projects/vdk-core/src/vdk/api/plugin/core_hook_spec.py#L95
-> why is vdk_configure and vdk_start in same class as they are used fully differently???


~~ for vdk_configure
-> why don't we have to separate vdk_configure and vdk_job_configure 
-> the first one is fully for vdk 
-> the second one is specific to a job 

Why do we use static methods in places liek this:
https://github.com/vmware/versatile-data-kit/blob/a45ee03578188b0445a823fdfe80a8a41f102ecf/projects/vdk-core/src/vdk/internal/builtin_plugins/config/log_config.py#L241



# db_connection_decorate_operation

hookimpl - vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin

# finalize_job

hookimpl - vdk.internal.builtin_plugins.notification.notification.NotificationPlugin
hookimpl - vdk.internal.builtin_plugins.ingestion.ingester_configuration_plugin.IngesterConfigurationPlugin

# initialize_job

hookimpl(trylast=True) - <vdk.internal.builtin_plugins.config.secrets_config.SecretsConfigPlugin object at 0x1284de390> # why is this trylast?
hookimpl - <vdk.plugin.test_utils.util_plugins.TestPropertiesPlugin object at 0x12849f3d0>
hookimpl - <vdk.plugin.test_utils.util_plugins.TestSecretsPlugin object at 0x12849ff90>
hookimpl - <vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x1284d0190> 
hookimpl - <vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x1284dc850> # why isn't this tryfirst? 
hookimpl - <vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x1284d0a10>  # why not tryfirst?
hookimpl - <vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x1284ebc90> #  again?
hookimpl - <vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x127d00b90> # why not trylast? 

When we change vdk_start in vdk-impala, we get this:
[<HookImpl plugin_name='140155530124544', plugin=<vdk.internal.builtin_plugins.config.secrets_config.SecretsConfigPlugin object at 0x7f7880961d00>>, 
<HookImpl plugin_name='140156326890752', plugin=<vdk.plugin.test_utils.util_plugins.TestPropertiesPlugin object at 0x7f78b013cd00>>, 
<HookImpl plugin_name='impala-plugin', plugin=<vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x7f78b97ac9d0>>,
<HookImpl plugin_name='140156484632736', plugin=<vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x7f78b97ac0a0>>,
<HookImpl plugin_name='140156484635232', plugin=<vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x7f78b97aca60>>, 
<HookImpl plugin_name='140156484635952', plugin=<vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x7f78b97acd30>>, 
<HookImpl plugin_name='140155530099152', plugin=<vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x7f788095b9d0>>, 
<HookImpl plugin_name='140155792708848', plugin=<vdk.internal.builtin_plugins.run.execution_tracking.ExecutionTrackingPlugin object at 0x7f78903cd4f0>>,
<HookImpl plugin_name='DataJobDefaultHookImplPlugin', plugin=<vdk.internal.builtin_plugins.run.data_job.DataJobDefaultHookImplPlugin object at 0x7f78903cd5e0>>]


# run_job

hookimpl(hookwrapper=True) - <vdk.internal.builtin_plugins.run.summary_output.JobRunSummaryOutputPlugin object at 0x127d01010>

# run_step

hookimpl(hookwrapper=True, tryfirst=True) -[staticmethod] <vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x127d00b90>

# vdk_cli_execute

hookimpl(trylast=True) - <vdk.internal.cli_entry.CliEntry object at 0x1284bccd0>
hookimpl(tryfirst=True) -<vdk.plugin.test_utils.util_funcs.TestingCliEntryPlugin object at 0x1284bd650>)

# vdk_command_line

hookimpl - <vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x127cfa750>
hookimpl - <vdk.internal.builtin_plugins.config.config_help.ConfigHelpPlugin object at 0x1284d23d0>
hookimpl - [staticmethod] <vdk.internal.builtin_plugins.connection.query_command_plugin.QueryCommandPlugin object at 0x127d00e50>
hookimpl - [staticmethod] <vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x12849eb10>
hookimpl(tryfirst=True) - <module 'vdk.internal.builtin_plugins.builtin_hook_impl' from '/Users/hduygu/...>


When we change vdk_start in vdk-impala, we get this:
[<HookImpl plugin_name='impala-plugin', plugin=<vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x7f78b97ac9d0>>,
<HookImpl plugin_name='140155792597776', plugin=<vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x7f78903b2310>>, 
<HookImpl plugin_name='140156484632688', plugin=<vdk.internal.builtin_plugins.config.config_help.ConfigHelpPlugin object at 0x7f78b97ac070>>,
<HookImpl plugin_name='140155530099056', plugin=<vdk.internal.builtin_plugins.connection.query_command_plugin.QueryCommandPlugin object at 0x7f788095b970>>, 
<HookImpl plugin_name='core-plugin', plugin=<module 'vdk.internal.builtin_plugins.builtin_hook_impl' from '/Users/hduygu/....>>]

# vdk_configure - look here https://github.com/vmware/versatile-data-kit/blob/a45ee03578188b0445a823fdfe80a8a41f102ecf/projects/vdk-core/src/vdk/internal/builtin_plugins/builtin_hook_impl.py#L119

hookimpl(trylast=True) - <vdk.internal.builtin_plugins.config.vdk_config.EnvironmentVarsConfigPlugin object at 0x127ce3490>
hookimpl - <vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x127ce3b90>
hookimpl - <vdk.internal.builtin_plugins.run.summary_output.JobRunSummaryOutputPlugin object at 0x127d01010>
hookimpl -[staticmethod] <vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x127d00b90>
hookimpl(tryfirst=True) - <vdk.internal.builtin_plugins.config.vdk_config.CoreConfigDefinitionPlugin object at 0x127ce3550>
hookimpl(tryfirst=True) - <vdk.internal.builtin_plugins.version.new_version_check_plugin.NewVersionCheckPlugin object at 0x127d00950>
hookimpl(tryfirst=True) - <vdk.internal.builtin_plugins.notification.notification.NotificationPlugin object at 0x127d009d0>
hookimpl(tryfirst=True) - <vdk.internal.builtin_plugins.ingestion.ingester_configuration_plugin.IngesterConfigurationPlugin object at 0x127d00790>
hookimpl(tryfirst=True) - <vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x127cf94d0>
hookimpl(tryfirst=True) - <vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x127d01550>
hookimpl(tryfirst=True) - <vdk.internal.builtin_plugins.config.vdk_config.JobConfigIniPlugin object at 0x127d00250>
hookimpl(tryfirst=True) - <vdk.internal.builtin_plugins.termination_message.writer.TerminationMessageWriterPlugin object at 0x127d01150>

When we change vdk_start in vdk-impala, we get this:
[<HookImpl plugin_name='140156484635328', plugin=<vdk.internal.builtin_plugins.config.vdk_config.EnvironmentVarsConfigPlugin object at 0x7f78b97acac0>>,
<HookImpl plugin_name='impala-plugin', plugin=<vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x7f78b97ac9d0>>, 
<HookImpl plugin_name='140156484632736', plugin=<vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x7f78b97ac0a0>>,
<HookImpl plugin_name='140155530124160', plugin=<vdk.internal.builtin_plugins.run.summary_output.JobRunSummaryOutputPlugin object at 0x7f7880961b80>>,
<HookImpl plugin_name='140156484635184', plugin=<vdk.internal.builtin_plugins.config.vdk_config.CoreConfigDefinitionPlugin object at 0x7f78b97aca30>>, 
<HookImpl plugin_name='140156484633120', plugin=<vdk.internal.builtin_plugins.version.new_version_check_plugin.NewVersionCheckPlugin object at 0x7f78b97ac220>>,
<HookImpl plugin_name='140156484634848', plugin=<vdk.internal.builtin_plugins.notification.notification.NotificationPlugin object at 0x7f78b97ac8e0>>,
<HookImpl plugin_name='140156484634944', plugin=<vdk.internal.builtin_plugins.ingestion.ingester_configuration_plugin.IngesterConfigurationPlugin object at 0x7f78b97ac940>>,
<HookImpl plugin_name='140156484635232', plugin=<vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x7f78b97aca60>>,
<HookImpl plugin_name='140156484635952', plugin=<vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x7f78b97acd30>>,
<HookImpl plugin_name='140156484635616', plugin=<vdk.internal.builtin_plugins.config.vdk_config.JobConfigIniPlugin object at 0x7f78b97acbe0>>, 
<HookImpl plugin_name='140155530125120', plugin=<vdk.internal.builtin_plugins.termination_message.writer.TerminationMessageWriterPlugin object at 0x7f7880961f40>>]


# vdk_exit

hookimpl - <vdk.internal.builtin_plugins.version.new_version_check_plugin.NewVersionCheckPlugin object at 0x127d00950>
hookimpl - <vdk.internal.builtin_plugins.notification.notification.NotificationPlugin object at 0x127d009d0>
hookimpl - <vdk.internal.builtin_plugins.termination_message.writer.TerminationMessageWriterPlugin object at 0x127d01150>

# vdk_initialize -> why isn't it trylast for every plugin? or why aren't all internal (vdk-core) plugins tryfirst? 

hookimpl(trylast=True) - <vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x127d00b90>
hookimpl - <vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x127cfa750>
hookimpl - <vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x127d00a90>
hookimpl(tryfirst=True) - <vdk.internal.builtin_plugins.builtin_hook_impl.RuntimeStateInitializePlugin object at 0x127ce35d0>

# vdk_main

hookimpl(trylast=True) - <vdk.internal.cli_entry.CliEntry object at 0x1284bccd0>

# vdk_start

hookimpl - <module 'vdk.plugin.impala.impala_plugin' from '/Users/hduygu/Documents/vdk/versatile-data-kit/projects/vdk-plugins/vdk-impala/src/vdk/plugin/impala/impala_plugin.py'>
hookimpl - <module 'vdk.internal.builtin_plugins.builtin_hook_impl' from '/Users/hduygu/Documents/vdk/versatile-data-kit/projects/vdk-core/src/vdk/internal/builtin_plugins/builtin_hook_impl.py'>
hookimpl - <vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x127cfa750>
hookimpl - <vdk.internal.builtin_plugins.config.vdk_config.JobConfigIniPlugin object at 0x127d00250>

