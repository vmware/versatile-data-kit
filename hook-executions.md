### <vdk.internal.cli_entry.CliEntry object at 0x1284bccd0>
@hookimpl(trylast=True)
def vdk_cli_execute

@hookimpl(trylast=True)
def vdk_main

### <vdk.plugin.test_utils.util_funcs.TestingCliEntryPlugin object at 0x1284bd650>)

@hookimpl(tryfirst=True)
def vdk_cli_execute

### <vdk.plugin.test_utils.util_plugins.TestPropertiesPlugin object at 0x12849f3d0>

@hookimpl
def initialize_job

### <vdk.plugin.test_utils.util_plugins.TestSecretsPlugin object at 0x12849ff90>

@hookimpl
def initialize_job

### ????????
'core-plugin'
PluginRegistry(group_name=vdk.plugin.run)Plugins: ('cli-entry', <vdk.internal.cli_entry.CliEntry object at 0x1284bccd0>)
('testing-cli-entry', <vdk.plugin.test_utils.util_funcs.TestingCliEntryPlugin object at 0x1284bd650>)
('4970902480', <vdk.plugin.test_utils.util_plugins.TestPropertiesPlugin object at 0x12849f3d0>)
('4970905488', <vdk.plugin.test_utils.util_plugins.TestSecretsPlugin object at 0x12849ff90>)
('vdk.plugin.impala.impala_plugin', <module 'vdk.plugin.impala.impala_plugin' from '/Users/hduygu/Documents/vdk/versatile-data-kit/projects/vdk-plugins/vdk-impala/src/vdk/plugin/impala/impala_plugin.py'>)

### ????????
PluginRegistry(group_name=vdk.plugin.run)Plugins: ('cli-entry', <vdk.internal.cli_entry.CliEntry object at 0x1284bccd0>)
('testing-cli-entry', <vdk.plugin.test_utils.util_funcs.TestingCliEntryPlugin object at 0x1284bd650>)
('4970902480', <vdk.plugin.test_utils.util_plugins.TestPropertiesPlugin object at 0x12849f3d0>)
('4970905488', <vdk.plugin.test_utils.util_plugins.TestSecretsPlugin object at 0x12849ff90>)
('vdk.plugin.impala.impala_plugin', <module 'vdk.plugin.impala.impala_plugin' from '/Users/hduygu/Documents/vdk/versatile-data-kit/projects/vdk-plugins/vdk-impala/src/vdk/plugin/impala/impala_plugin.py'>)
('core-plugin', <module 'vdk.internal.builtin_plugins.builtin_hook_impl' from '/Users/hduygu/Documents/vdk/versatile-data-kit/projects/vdk-core/src/vdk/internal/builtin_plugins/builtin_hook_impl.py'>)

### <vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x1284d0190>

@staticmethod
@hookimpl
def vdk_configure

@hookimpl
def initialize_job

### <vdk.internal.builtin_plugins.config.config_help.ConfigHelpPlugin object at 0x1284d23d0>

@hookimpl
def vdk_command_line

### <vdk.internal.builtin_plugins.config.vdk_config.CoreConfigDefinitionPlugin object at 0x12844f150>

@hookimpl(tryfirst=True)
def vdk_configure

### <vdk.internal.builtin_plugins.config.vdk_config.EnvironmentVarsConfigPlugin object at 0x1284bd690>

@hookimpl(trylast=True)
def vdk_configure

### <vdk.internal.builtin_plugins.builtin_hook_impl.RuntimeStateInitializePlugin object at 0x1284bfc50>

@hookimpl(tryfirst=True)
def vdk_initialize

### <vdk.internal.builtin_plugins.version.new_version_check_plugin.NewVersionCheckPlugin object at 0x1284644d0>

@hookimpl(tryfirst=True)
def vdk_configure

@hookimpl
def vdk_exit

### <vdk.internal.builtin_plugins.notification.notification.NotificationPlugin object at 0x1284d2a90>

@hookimpl(tryfirst=True)
def vdk_configure

@hookimpl
def finalize_job

@hookimpl
def vdk_exit

### <vdk.internal.builtin_plugins.ingestion.ingester_configuration_plugin.IngesterConfigurationPlugin object at 0x1284dc290>

@hookimpl(tryfirst=True)
def vdk_configure

@hookimpl
def finalize_job

### <vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x1284dc850>

@hookimpl(tryfirst=True)
def vdk_configure

@hookimpl
def initialize_job

### <vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x1284d0a10>

@hookimpl(tryfirst=True)
def vdk_configure

@hookimpl
def initialize_job

### <vdk.internal.builtin_plugins.config.vdk_config.JobConfigIniPlugin object at 0x1284d0d10>

@hookimpl
def vdk_start

@hookimpl(tryfirst=True)
def vdk_configure

### <vdk.internal.builtin_plugins.config.secrets_config.SecretsConfigPlugin object at 0x1284de390>

@hookimpl(trylast=True)
def initialize_job

### <vdk.internal.builtin_plugins.termination_message.writer.TerminationMessageWriterPlugin object at 0x126ad1990>

@hookimpl(tryfirst=True)
def vdk_configure

@hookimpl
def vdk_exit

### <vdk.internal.builtin_plugins.run.summary_output.JobRunSummaryOutputPlugin object at 0x1284d2910>

@hookimpl
def vdk_configure

@hookimpl(hookwrapper=True)
def run_job

### <vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x1284ebc90>

@hookimpl
def initialize_job

@hookimpl
def vdk_initialize

@hookimpl
def db_connection_decorate_operation

### <vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x12849eb10>

@staticmethod
@hookimpl
def vdk_configure

@staticmethod
@hookimpl
def vdk_command_line

@hookimpl(trylast=True)  
def vdk_initialize

@hookimpl
def initialize_job

@staticmethod
@hookimpl(hookwrapper=True, tryfirst=True)
def run_step

@hookimpl
def vdk_start

### <vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x127cfa750>

@hookimpl
def vdk_start

@hookimpl
def vdk_initialize

@hookimpl
def vdk_command_line

### <vdk.internal.builtin_plugins.connection.query_command_plugin.QueryCommandPlugin object at 0x127d00e50>

@staticmethod
@hookimpl
def vdk_command_line

## hook()

#### <HookCaller 'db_connection_decorate_operation'>
[<HookImpl plugin_name='4962912912', plugin=<vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x127d00a90>>]


#### <HookCaller 'finalize_job'>
[<HookImpl plugin_name='4962912720', plugin=<vdk.internal.builtin_plugins.notification.notification.NotificationPlugin object at 0x127d009d0>>, 
<HookImpl plugin_name='4962912144', plugin=<vdk.internal.builtin_plugins.ingestion.ingester_configuration_plugin.IngesterConfigurationPlugin object at 0x127d00790>>]


#### <HookCaller 'initialize_job'>
[<HookImpl plugin_name='4962914704', plugin=<vdk.internal.builtin_plugins.config.secrets_config.SecretsConfigPlugin object at 0x127d01190>>, 
<HookImpl plugin_name='4962692816', plugin=<vdk.plugin.test_utils.util_plugins.TestPropertiesPlugin object at 0x127ccaed0>>, 
<HookImpl plugin_name='4962696592', plugin=<vdk.plugin.test_utils.util_plugins.TestSecretsPlugin object at 0x127ccbd90>>, 
<HookImpl plugin_name='4962794384', plugin=<vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x127ce3b90>>,
<HookImpl plugin_name='4962882768', plugin=<vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x127cf94d0>>,
<HookImpl plugin_name='4962915664', plugin=<vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x127d01550>>,
<HookImpl plugin_name='4962912912', plugin=<vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x127d00a90>>, 
<HookImpl plugin_name='impala-plugin', plugin=<vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x127d00b90>>]


#### <HookCaller 'run_job'>
[<HookImpl plugin_name='4962914320', plugin=<vdk.internal.builtin_plugins.run.summary_output.JobRunSummaryOutputPlugin object at 0x127d01010>>]

#### <HookCaller 'run_step'>
[<HookImpl plugin_name='impala-plugin', plugin=<vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x127d00b90>>]

#### <HookCaller 'vdk_cli_execute'>
[<HookImpl plugin_name='cli-entry', plugin=<vdk.internal.cli_entry.CliEntry object at 0x127ce0b90>>, 
<HookImpl plugin_name='testing-cli-entry', plugin=<vdk.plugin.test_utils.util_funcs.TestingCliEntryPlugin object at 0x127ce0c90>>]

#### <HookCaller 'vdk_command_line'>
[<HookImpl plugin_name='4962887504', plugin=<vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x127cfa750>>, 
<HookImpl plugin_name='4962794320', plugin=<vdk.internal.builtin_plugins.config.config_help.ConfigHelpPlugin object at 0x127ce3b50>>,
<HookImpl plugin_name='4962913872', plugin=<vdk.internal.builtin_plugins.connection.query_command_plugin.QueryCommandPlugin object at 0x127d00e50>>,
<HookImpl plugin_name='impala-plugin', plugin=<vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x127d00b90>>, 
<HookImpl plugin_name='core-plugin', plugin=<module 'vdk.internal.builtin_plugins.builtin_hook_impl' from '/Users/hduygu/Documents/vdk/versatile-data-kit/projects/vdk-core/src/vdk/internal/builtin_plugins/builtin_hook_impl.py'>>]

#### <HookCaller 'vdk_configure'>
[<HookImpl plugin_name='4962792592', plugin=<vdk.internal.builtin_plugins.config.vdk_config.EnvironmentVarsConfigPlugin object at 0x127ce3490>>, 
<HookImpl plugin_name='4962794384', plugin=<vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x127ce3b90>>,
<HookImpl plugin_name='4962914320', plugin=<vdk.internal.builtin_plugins.run.summary_output.JobRunSummaryOutputPlugin object at 0x127d01010>>,
<HookImpl plugin_name='impala-plugin', plugin=<vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x127d00b90>>,
<HookImpl plugin_name='4962792784', plugin=<vdk.internal.builtin_plugins.config.vdk_config.CoreConfigDefinitionPlugin object at 0x127ce3550>>, 
<HookImpl plugin_name='4962912592', plugin=<vdk.internal.builtin_plugins.version.new_version_check_plugin.NewVersionCheckPlugin object at 0x127d00950>>,
<HookImpl plugin_name='4962912720', plugin=<vdk.internal.builtin_plugins.notification.notification.NotificationPlugin object at 0x127d009d0>>,
<HookImpl plugin_name='4962912144', plugin=<vdk.internal.builtin_plugins.ingestion.ingester_configuration_plugin.IngesterConfigurationPlugin object at 0x127d00790>>, 
<HookImpl plugin_name='4962882768', plugin=<vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x127cf94d0>>,
<HookImpl plugin_name='4962915664', plugin=<vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x127d01550>>,
<HookImpl plugin_name='4962910800', plugin=<vdk.internal.builtin_plugins.config.vdk_config.JobConfigIniPlugin object at 0x127d00250>>,
<HookImpl plugin_name='4962914640', plugin=<vdk.internal.builtin_plugins.termination_message.writer.TerminationMessageWriterPlugin object at 0x127d01150>>]

#### <HookCaller 'vdk_exit'>
[<HookImpl plugin_name='4962912592', plugin=<vdk.internal.builtin_plugins.version.new_version_check_plugin.NewVersionCheckPlugin object at 0x127d00950>>,
<HookImpl plugin_name='4962912720', plugin=<vdk.internal.builtin_plugins.notification.notification.NotificationPlugin object at 0x127d009d0>>,
<HookImpl plugin_name='4962914640', plugin=<vdk.internal.builtin_plugins.termination_message.writer.TerminationMessageWriterPlugin object at 0x127d01150>>]

#### <HookCaller 'vdk_initialize'>
[<HookImpl plugin_name='impala-plugin', plugin=<vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x127d00b90>>,
<HookImpl plugin_name='4962887504', plugin=<vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x127cfa750>>, 
<HookImpl plugin_name='4962912912', plugin=<vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x127d00a90>>,
<HookImpl plugin_name='4962792912', plugin=<vdk.internal.builtin_plugins.builtin_hook_impl.RuntimeStateInitializePlugin object at 0x127ce35d0>>]

#### <HookCaller 'vdk_main'>
[<HookImpl plugin_name='cli-entry', plugin=<vdk.internal.cli_entry.CliEntry object at 0x127ce0b90>>]

#### <HookCaller 'vdk_start'>
[<HookImpl plugin_name='vdk.plugin.impala.impala_plugin', plugin=<module 'vdk.plugin.impala.impala_plugin' from '/Users/hduygu/Documents/vdk/versatile-data-kit/projects/vdk-plugins/vdk-impala/src/vdk/plugin/impala/impala_plugin.py'>>,
<HookImpl plugin_name='core-plugin', plugin=<module 'vdk.internal.builtin_plugins.builtin_hook_impl' from '/Users/hduygu/Documents/vdk/versatile-data-kit/projects/vdk-core/src/vdk/internal/builtin_plugins/builtin_hook_impl.py'>>, 
<HookImpl plugin_name='4962887504', plugin=<vdk.internal.builtin_plugins.debug.debug.DebugPlugins object at 0x127cfa750>>,
<HookImpl plugin_name='4962910800', plugin=<vdk.internal.builtin_plugins.config.vdk_config.JobConfigIniPlugin object at 0x127d00250>>]