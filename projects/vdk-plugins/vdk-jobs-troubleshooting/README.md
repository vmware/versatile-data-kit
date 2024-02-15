## VDK-JOBS-TROUBLESHOOTING Plugin

<a href="https://pypistats.org/packages/vdk-jobs-troubleshooting" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-jobs-troubleshooting.svg" alt="monthly download count for vdk-jobs-troubleshooting"></a>

The VDK JOB Troubleshooting plugin provides the ability to add various troubleshooting utilities which can be accessed
during the data job runtime.

Generally it's quite hard to produce a thread dump of a python process running inside a kubernetes pod. So this plugin
provides a thread-dump utility

### Adding the plugin to your data job

Before you can use the plugin you should add it to your data job or custom-sdk, by adding the following line to your
requirements.txt file:

```commandline
vdk-jobs-troubleshooting
```

Next you need to add the list of utilities to use to your data job configuration. For example, to enable the thread-dump
utility you have to add the following to your data job's config.ini file.

```properties
[vdk]

TROUBLESHOOT_UTILITIES_TO_USE=thread-dump
```

### Getting a thread dump from a running job

During the startup of the data job the troubleshooting utility will log a message with the port it is running on. Example:

```commandline
Troubleshooting utility server will start on port 8783.
```

So in order to get a thread dump from the running data job do the following.

1. Review the logs (using the kubectl logs pod/<data job pod it> command ) and find the troubleshooting utility port
2. Start a port forward from your local machine to the target pod and port for example

```commandline
kubectl port-forward pods/my-problematic-job-1691419320-jcsn7 8783:8783
```

3. In a new/different console execute a curl command, to the pod. Example

```commandline
curl localhost:8783/threads
```

The thread-dump will be printed in the console.
<details>
  <summary>Sample output</summary>

<pre>
Thread:MainThread alive:True daemon:False
Thread:troubleshooting_utility alive:True daemon:True
Thread:payload-aggregator alive:True daemon:True
Thread:payload-poster0 alive:True daemon:True
Thread:ThreadPoolExecutor-0_0 alive:True daemon:True
Thread:payload-aggregator alive:True daemon:True
Thread:payload-poster0 alive:True daemon:True
...
Thread:payload-poster9 alive:True daemon:True
Thread:troubleshooting_utility alive:True daemon:True
 # ThreadID: 140056075323136
 /usr/local/lib/python3.7/threading.py::890::_bootstrap::self._bootstrap_inner()
 /usr/local/lib/python3.7/threading.py::926::_bootstrap_inner::self.run()
 /usr/local/lib/python3.7/threading.py::870::run::self._target(*self._args, **self._kwargs)
 /usr/local/lib/python3.7/socketserver.py::232::serve_forever::ready = selector.select(poll_interval)
 /usr/local/lib/python3.7/selectors.py::415::select::fd_event_list = self._selector.poll(timeout)
 # ThreadID: 140054872303360
...
 # ThreadID: 140055860274944
 /usr/local/lib/python3.7/threading.py::890::_bootstrap::self._bootstrap_inner()
 /usr/local/lib/python3.7/threading.py::926::_bootstrap_inner::self.run()
 /usr/local/lib/python3.7/threading.py::870::run::self._target(*self._args, **self._kwargs)
 /usr/local/lib/python3.7/socketserver.py::237::serve_forever::self._handle_request_noblock()
 /usr/local/lib/python3.7/socketserver.py::316::_handle_request_noblock::self.process_request(request, client_address)
 /usr/local/lib/python3.7/socketserver.py::347::process_request::self.finish_request(request, client_address)
 /usr/local/lib/python3.7/socketserver.py::360::finish_request::self.RequestHandlerClass(request, client_address, self)
 /usr/local/lib/python3.7/socketserver.py::720::__init__::self.handle()
 /usr/local/lib/python3.7/http/server.py::434::handle::self.handle_one_request()
 /usr/local/lib/python3.7/http/server.py::422::handle_one_request::method()
 /vdk/site-packages/vdk/plugin/jobs_troubleshoot/troubleshoot_utilities/thread_dump.py::36::do_GET::self._log_thread_dump()
 /vdk/site-packages/vdk/plugin/jobs_troubleshoot/troubleshoot_utilities/thread_dump.py::58::_log_thread_dump::for filename, lineno, name, line in traceback.extract_stack(stack):
 # ThreadID: 140056193533760
 /vdk/vdk::8::<module>::sys.exit(main())
 /vdk/site-packages/vdk/internal/cli_entry.py::186::main::command_line_args=sys.argv[1:],
 /vdk/site-packages/pluggy/_hooks.py::433::__call__::return self._hookexec(self.name, self._hookimpls, kwargs, firstresult)
 /vdk/site-packages/pluggy/_manager.py::112::_hookexec::return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
 /vdk/site-packages/pluggy/_callers.py::80::_multicall::res = hook_impl.function(*args)
 /vdk/site-packages/vdk/internal/cli_entry.py::140::vdk_main::program_name=program_name,
 /vdk/site-packages/pluggy/_hooks.py::433::__call__::return self._hookexec(self.name, self._hookimpls, kwargs, firstresult)
 /vdk/site-packages/pluggy/_manager.py::112::_hookexec::return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
 /vdk/site-packages/pluggy/_callers.py::80::_multicall::res = hook_impl.function(*args)
 /vdk/site-packages/vdk/internal/cli_entry.py::100::vdk_cli_execute::obj=core_context,
 /vdk/site-packages/click/core.py::1157::__call__::return self.main(*args, **kwargs)
 /vdk/site-packages/click/core.py::1078::main::rv = self.invoke(ctx)
 /vdk/site-packages/click/core.py::1688::invoke::return _process_result(sub_ctx.command.invoke(sub_ctx))
 /vdk/site-packages/click/core.py::1434::invoke::return ctx.invoke(self.callback, **ctx.params)
 /vdk/site-packages/click/core.py::783::invoke::return __callback(*args, **kwargs)
 /vdk/site-packages/click/decorators.py::33::new_func::return f(get_current_context(), *args, **kwargs)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/cli_run.py::221::run::context, pathlib.Path(data_job_directory), arguments
 /vdk/site-packages/vdk/internal/builtin_plugins/run/cli_run.py::143::create_and_run_data_job::execution_result = job.run(args)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/data_job.py::312::run::return self._plugin_hook.run_job(context=job_context)
 /vdk/site-packages/pluggy/_hooks.py::433::__call__::return self._hookexec(self.name, self._hookimpls, kwargs, firstresult)
 /vdk/site-packages/pluggy/_manager.py::112::_hookexec::return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
 /vdk/site-packages/pluggy/_callers.py::80::_multicall::res = hook_impl.function(*args)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/data_job.py::142::run_job::context=context, step=current_step
 /vdk/site-packages/pluggy/_hooks.py::433::__call__::return self._hookexec(self.name, self._hookimpls, kwargs, firstresult)
 /vdk/site-packages/pluggy/_manager.py::112::_hookexec::return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
 /vdk/site-packages/pluggy/_callers.py::80::_multicall::res = hook_impl.function(*args)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/data_job.py::73::run_step::step_executed = step.runner_func(step, context.job_input)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/file_based_step.py::103::run_python_step::StepFuncFactory.invoke_run_function(func, job_input, step.name)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/file_based_step.py::139::invoke_run_function::func(**actual_arguments)
 /job/starshot-prod-processing-csp-jira/common_library/send_slack_msg_on_job_failure.py::12::run::return func(job_input) /job/starshot-prod-processing-csp-jira/processing-csp-jira.py::8::run::load_dw_objects(job_input, dw_objects_to_load)
 /job/starshot-prod-processing-csp-jira/common_library/processing_templates.py::60::load_dw_objects::additional_params=additional_params
 /job/starshot-prod-processing-csp-jira/common_library/processing_templates.py::36::load_dw_object::template_args=template_parameters
 /vdk/site-packages/supercollider/vdk/telemetry/telemetry_plugin.py::83::execute_template::return core_execute_template(template_name, template_args)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/job_input.py::167::execute_template::result = self.__templates.execute_template(template_name, template_args)
 /vdk/site-packages/vdk/internal/builtin_plugins/templates/template_impl.py::53::execute_template::result = template_job.run(template_args, name)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/data_job.py::312::run::return self._plugin_hook.run_job(context=job_context)
 /vdk/site-packages/pluggy/_hooks.py::433::__call__::return self._hookexec(self.name, self._hookimpls, kwargs, firstresult)
 /vdk/site-packages/pluggy/_manager.py::112::_hookexec::return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
 /vdk/site-packages/pluggy/_callers.py::80::_multicall::res = hook_impl.function(*args)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/data_job.py::142::run_job::context=context, step=current_step
 /vdk/site-packages/pluggy/_hooks.py::433::__call__::return self._hookexec(self.name, self._hookimpls, kwargs, firstresult)
 /vdk/site-packages/pluggy/_manager.py::112::_hookexec::return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
 /vdk/site-packages/pluggy/_callers.py::80::_multicall::res = hook_impl.function(*args)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/data_job.py::73::run_step::step_executed = step.runner_func(step, context.job_input)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/file_based_step.py::103::run_python_step::StepFuncFactory.invoke_run_function(func, job_input, step.name)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/file_based_step.py::139::invoke_run_function::func(**actual_arguments)
 /vdk/site-packages/vdk/plugin/impala/templates/load/dimension/scd1/02-handle-quality-checks.py::59::run::job_input.execute_query(insert_into_target)
 /vdk/site-packages/vdk/internal/builtin_plugins/run/job_input.py::127::execute_query::return connection.execute_query(query)
 /vdk/site-packages/vdk/internal/builtin_plugins/connection/managed_connection_base.py::120::execute_query::cur.execute(query)
 /vdk/site-packages/vdk/internal/builtin_plugins/connection/managed_cursor.py::96::execute::result = self._execute_operation(managed_operation)
 /vdk/site-packages/vdk/internal/builtin_plugins/connection/managed_cursor.py::168::_execute_operation::execution_cursor=execution_cursor
 /vdk/site-packages/pluggy/_hooks.py::433::__call__::return self._hookexec(self.name, self._hookimpls, kwargs, firstresult)
 /vdk/site-packages/pluggy/_manager.py::112::_hookexec::return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
 /vdk/site-packages/pluggy/_callers.py::80::_multicall::res = hook_impl.function(*args)
 /vdk/site-packages/vdk/internal/builtin_plugins/connection/connection_hooks.py::33::db_connection_execute_operation::native_result = execution_cursor.execute(managed_operation.get_operation())
 /vdk/site-packages/vdk/internal/builtin_plugins/connection/pep249/interfaces.py::64::execute::return self._cursor.execute(operation)
 /vdk/site-packages/impala/hiveserver2.py::343::execute::self._wait_to_finish()  # make execute synchronous
 /vdk/site-packages/impala/hiveserver2.py::438::_wait_to_finish::time.sleep(self._get_sleep_interval(loop_start))
</pre>
</details>
