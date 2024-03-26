
# db_connection_decorate_operation

hookimpl - vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin

# finalize_job

hookimpl - vdk.internal.builtin_plugins.notification.notification.NotificationPlugi
hookimpl - vdk.internal.builtin_plugins.ingestion.ingester_configuration_plugin.IngesterConfigurationPlugin

# initialize_job

hookimpl(trylast=True) - <vdk.internal.builtin_plugins.config.secrets_config.SecretsConfigPlugin object at 0x1284de390>
hookimpl - <vdk.plugin.test_utils.util_plugins.TestPropertiesPlugin object at 0x12849f3d0>
hookimpl - <vdk.plugin.test_utils.util_plugins.TestSecretsPlugin object at 0x12849ff90>
hookimpl - <vdk.internal.builtin_plugins.config.log_config.LoggingPlugin object at 0x1284d0190>
hookimpl - <vdk.internal.builtin_plugins.job_properties.properties_api_plugin.PropertiesApiPlugin object at 0x1284dc850>
hookimpl - <vdk.internal.builtin_plugins.job_secrets.secrets_api_plugin.SecretsApiPlugin object at 0x1284d0a10>
hookimpl - <vdk.internal.builtin_plugins.connection.connection_plugin.QueryDecoratorPlugin object at 0x1284ebc90>
hookimpl - <vdk.plugin.impala.impala_plugin.ImpalaPlugin object at 0x127d00b90>

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

# vdk_configure

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

# vdk_exit

hookimpl - <vdk.internal.builtin_plugins.version.new_version_check_plugin.NewVersionCheckPlugin object at 0x127d00950>
hookimpl - <vdk.internal.builtin_plugins.notification.notification.NotificationPlugin object at 0x127d009d0>
hookimpl - <vdk.internal.builtin_plugins.termination_message.writer.TerminationMessageWriterPlugin object at 0x127d01150>

# vdk_initialize

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

