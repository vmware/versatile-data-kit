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

hookimpl(trylast=True) - <vdk.internal.builtin_plugins.config.secrets_config.SecretsConfigPlugin object at 0x1284de390> # no reason to have it trylast we just want it to be after SecretsApiPlugin
hookimpl - <vdk.plugin.test_utils.util_plugins.TestPropertiesPlugin object at 0x12849f3d0>
hookimpl - <vdk.plugin.test_utils.util_plugins.TestSecretsPlugin object at 0x12849ff90>
hookimpl - <vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x1284d0190> 
hookimpl - <vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x1284dc850> \
hookimpl - <vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x1284d0a10>  
hookimpl - <vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x1284ebc90> 
hookimpl - <vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x127d00b90> 


After core changes:
[
hookimpl - <HookImpl plugin_name='4821314832', plugin=<vdk.plugin.test_utils.util_plugins.TestPropertiesPlugin object at 0x11f5f6d10>>,
hookimpl - <HookImpl plugin_name='4821315280', plugin=<vdk.plugin.test_utils.util_plugins.TestSecretsPlugin object at 0x11f5f6ed0>>,
hookimpl - <HookImpl plugin_name='impala-plugin', plugin=<vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x11f4e4f50>>,
hookimpl - <HookImpl plugin_name='4820263568', plugin=<vdk.internal.builtin_plugins.config.secrets_config.SecretsConfigPlugin object at 0x11f4f6290>>,
hookimpl - <HookImpl plugin_name='4821460816', plugin=<vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x11f61a750>>,
hookimpl - <HookImpl plugin_name='4821459408', plugin=<vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x11f61a1d0>>,
hookimpl - <HookImpl plugin_name='4821393168', plugin=<vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x11f609f10>>,
hookimpl - <HookImpl plugin_name='4820015440', plugin=<vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x11f4b9950>>,
hookimpl - <HookImpl plugin_name='4822942160', plugin=<vdk.internal.builtin_plugins.run.execution_tracking.ExecutionTrackingPlugin object at 0x11f7841d0>>,
hookimpl - <HookImpl plugin_name='DataJobDefaultHookImplPlugin', plugin=<vdk.internal.builtin_plugins.run.data_job.DataJobDefaultHookImplPlugin object at 0x11f7755d0>>]



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

After core changes:
[
hookimpl(trylast=True) - <HookImpl plugin_name='4820066128', plugin=<vdk.internal.builtin_plugins.config.vdk_config.EnvironmentVarsConfigPlugin object at 0x11f4c5f50>>,
hookimpl - <HookImpl plugin_name='impala-plugin', plugin=<vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x11f4e4f50>>,
hookimpl - <HookImpl plugin_name='4821460816', plugin=<vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x11f61a750>>,
hookimpl - <HookImpl plugin_name='4821365712', plugin=<vdk.internal.builtin_plugins.run.summary_output.JobRunSummaryOutputPlugin object at 0x11f6033d0>>,
hookimpl - <HookImpl plugin_name='4821398416', plugin=<vdk.internal.builtin_plugins.version.new_version_check_plugin.NewVersionCheckPlugin object at 0x11f60b390>>,
hookimpl - <HookImpl plugin_name='4821270928', plugin=<vdk.internal.builtin_plugins.notification.notification.NotificationPlugin object at 0x11f5ec190>>,
hookimpl - <HookImpl plugin_name='4821309904', plugin=<vdk.internal.builtin_plugins.ingestion.ingester_configuration_plugin.IngesterConfigurationPlugin object at 0x11f5f59d0>>,
hookimpl - <HookImpl plugin_name='4821393168', plugin=<vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x11f609f10>>,
hookimpl - <HookImpl plugin_name='4820015440', plugin=<vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x11f4b9950>>,
hookimpl - <HookImpl plugin_name='4821393104', plugin=<vdk.internal.builtin_plugins.config.vdk_config.JobConfigIniPlugin object at 0x11f609ed0>>,
hookimpl - <HookImpl plugin_name='4820890768', plugin=<vdk.internal.builtin_plugins.termination_message.writer.TerminationMessageWriterPlugin object at 0x11f58f490>>,
hookimpl - <HookImpl plugin_name='4821365520', plugin=<vdk.internal.builtin_plugins.config.vdk_config.CoreConfigDefinitionPlugin object at 0x11f603310>>]

When we change vdk_start(tryfirst) in vdk-impala, we get this:
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

with changes in core
[
hookimpl(trylast=true) - <HookImpl plugin_name='impala-plugin', plugin=<vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x7fc3698e2100>>,
hookimpl - <HookImpl plugin_name='140477266208320', plugin=<vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x7fc3698d2640>>,
hookimpl - <HookImpl plugin_name='140477266275344', plugin=<vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x7fc3698e2c10>>,
hookimpl - <HookImpl plugin_name='140477266273376', plugin=<vdk.internal.builtin_plugins.builtin_hook_impl.RuntimeStateInitializePlugin object at 0x7fc3698e2460>>]

# vdk_main

hookimpl(trylast=True) - <vdk.internal.cli_entry.CliEntry object at 0x1284bccd0>

# vdk_start

hookimpl - <module 'vdk.plugin.impala.impala_plugin' from '/Users/hduygu/Documents/vdk/versatile-data-kit/projects/vdk-plugins/vdk-impala/src/vdk/plugin/impala/impala_plugin.py'>
hookimpl - <module 'vdk.internal.builtin_plugins.builtin_hook_impl' from '/Users/hduygu/Documents/vdk/versatile-data-kit/projects/vdk-core/src/vdk/internal/builtin_plugins/builtin_hook_impl.py'>
hookimpl - <vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x127cfa750>
hookimpl - <vdk.internal.builtin_plugins.config.vdk_config.JobConfigIniPlugin object at 0x127d00250>

[
hookimpl(trylast=true) - <HookImpl plugin_name='core-plugin', plugin=<module 'vdk.internal.builtin_plugins.builtin_hook_impl' from '/Users/hduygu/....'>>,
hookimpl - <HookImpl plugin_name='vdk.plugin.impala.impala_plugin', plugin=<module 'vdk.plugin.impala.impala_plugin' from '/Users/hduygu....'>>,
hookimpl - <HookImpl plugin_name='4817281616', plugin=<vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x11f21e250>>,
hookimpl - <HookImpl plugin_name='4821393104', plugin=<vdk.internal.builtin_plugins.config.vdk_config.JobConfigIniPlugin object at 0x11f609ed0>>]


# Oracle

Current behaviour: 

##  initialize_job

[<HookImpl plugin_name='OraclePlugin', plugin=<vdk.plugin.oracle.oracle_plugin.OraclePlugin object at 0x7f9850f34ca0>>,
<HookImpl plugin_name='140292169879408', plugin=<vdk.internal.builtin_plugins.config.secrets_config.SecretsConfigPlugin object at 0x7f9850f34f70>>, 
<HookImpl plugin_name='140292169878016', plugin=<vdk.plugin.test_utils.util_plugins.TestPropertiesPlugin object at 0x7f9850f34a00>>, 
<HookImpl plugin_name='140292169964320', plugin=<vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x7f9850f49b20>>, 
<HookImpl plugin_name='140292169962880', plugin=<vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x7f9850f49580>>, 
<HookImpl plugin_name='140292169879168', plugin=<vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x7f9850f34e80>>,
<HookImpl plugin_name='140292169876624', plugin=<vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x7f9850f34490>>, 
<HookImpl plugin_name='140293243246000', plugin=<vdk.internal.builtin_plugins.run.execution_tracking.ExecutionTrackingPlugin object at 0x7f9890ed95b0>>,
<HookImpl plugin_name='DataJobDefaultHookImplPlugin', plugin=<vdk.internal.builtin_plugins.run.data_job.DataJobDefaultHookImplPlugin object at 0x7f9850b00940>>]

# vdk+start
[<HookImpl plugin_name='vdk.plugin.oracle.oracle_plugin', plugin=<module 'vdk.plugin.oracle.oracle_plugin' from '/Users/hduygu/Documents/vdk/versatile-data-kit/projects/vdk-plugins/vdk-oracle/src/vdk/plugin/oracle/oracle_plugin.py'>>,
<HookImpl plugin_name='core-plugin', plugin=<module 'vdk.internal.builtin_plugins.builtin_hook_impl' from '/Users/hduygu/opt/anaconda3/envs/vdk-jupyter-2/lib/python3.9/site-packages/vdk/internal/builtin_plugins/builtin_hook_impl.py'>>, 
<HookImpl plugin_name='140292169962112', plugin=<vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x7f9850f49280>>,
<HookImpl plugin_name='140292169878976', plugin=<vdk.internal.builtin_plugins.config.vdk_config.JobConfigIniPlugin object at 0x7f9850f34dc0>>]

If we remove the trylast in oracle initialize: 

## initialize_job
[<HookImpl plugin_name='140274044683840', plugin=<vdk.internal.builtin_plugins.config.secrets_config.SecretsConfigPlugin object at 0x7f94189ac640>>,
<HookImpl plugin_name='140273901545552', plugin=<vdk.plugin.test_utils.util_plugins.TestPropertiesPlugin object at 0x7f941012a850>>,
<HookImpl plugin_name='140274044684752', plugin=<vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x7f94189ac9d0>>, 
<HookImpl plugin_name='140274044682784', plugin=<vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x7f94189ac220>>, 
<HookImpl plugin_name='140274044685520', plugin=<vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x7f94189accd0>>,
<HookImpl plugin_name='140274044686288', plugin=<vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x7f94189acfd0>>, 
<HookImpl plugin_name='OraclePlugin', plugin=<vdk.plugin.oracle.oracle_plugin.OraclePlugin object at 0x7f94189acee0>>, 
<HookImpl plugin_name='140273901546032', plugin=<vdk.internal.builtin_plugins.run.execution_tracking.ExecutionTrackingPlugin object at 0x7f941012aa30>>,
<HookImpl plugin_name='DataJobDefaultHookImplPlugin', plugin=<vdk.internal.builtin_plugins.run.data_job.DataJobDefaultHookImplPlugin object at 0x7f9418913d60>>]

# vdk_start
[<HookImpl plugin_name='vdk.plugin.oracle.oracle_plugin', plugin=<module 'vdk.plugin.oracle.oracle_plugin' from '/Users/hduygu/Documents/vdk/versatile-data-kit/projects/vdk-plugins/vdk-oracle/src/vdk/plugin/oracle/oracle_plugin.py'>>, 
<HookImpl plugin_name='core-plugin', plugin=<module 'vdk.internal.builtin_plugins.builtin_hook_impl' from '/Users/hduygu/opt/anaconda3/envs/vdk-jupyter-2/lib/python3.9/site-packages/vdk/internal/builtin_plugins/builtin_hook_impl.py'>>, 
<HookImpl plugin_name='140274044684512', plugin=<vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x7f94189ac8e0>>, 
<HookImpl plugin_name='140274044685568', plugin=<vdk.internal.builtin_plugins.config.vdk_config.JobConfigIniPlugin object at 0x7f94189acd00>>]

If we add tryfirst to vdk_start and remove trylast in initialize_job in oracle:

## initialize_job
[<HookImpl plugin_name='140529876444880', plugin=<vdk.internal.builtin_plugins.config.secrets_config.SecretsConfigPlugin object at 0x7fcfa95da6d0>>, 
<HookImpl plugin_name='140529472561456', plugin=<vdk.plugin.test_utils.util_plugins.TestPropertiesPlugin object at 0x7fcf914ae130>>,
<HookImpl plugin_name='OraclePlugin', plugin=<vdk.plugin.oracle.oracle_plugin.OraclePlugin object at 0x7fcfa95da880>>,
<HookImpl plugin_name='140529472563616', plugin=<vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x7fcf914ae9a0>>,
<HookImpl plugin_name='140529876444400', plugin=<vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x7fcfa95da4f0>>,
<HookImpl plugin_name='140529876444640', plugin=<vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x7fcfa95da5e0>>, 
<HookImpl plugin_name='140529876445936', plugin=<vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x7fcfa95daaf0>>,
<HookImpl plugin_name='140529875826912', plugin=<vdk.internal.builtin_plugins.run.execution_tracking.ExecutionTrackingPlugin object at 0x7fcfa95438e0>>,
<HookImpl plugin_name='DataJobDefaultHookImplPlugin', plugin=<vdk.internal.builtin_plugins.run.data_job.DataJobDefaultHookImplPlugin object at 0x7fcfa95dcdf0>>]

