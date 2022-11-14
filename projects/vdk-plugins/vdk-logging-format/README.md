This plugins allows for the configuration of the format of VDK logs.

# TEXT

This is the default log format, and is the one which VDK would use if vdk-logging-format is not installed.
It is intended to be human-readable; it is not structured in an easy-to-parse way for a machine.

Logs appear in the following format:
```
2022-11-11 15:22:43,863 [VDK] example-job [INFO ] root                              execution_skip.py:111  _skip_job_if_nec[id:baf3c02e-eef0-4b6f-9abe-438177967621-1668172963-1d1fe]- Local execution, skipping parallel execution check.
2022-11-11 15:22:43,864 [VDK] example-job [INFO ] vdk.internal.builtin_plugins.r   file_based_step.py:102  run_python_step [id:baf3c02e-eef0-4b6f-9abe-438177967621-1668172963-1d1fe]- Entering 10.py#run(...) ...
```

# LTSV

This is a POC level implementation of a plugin which changes the logging format of vdk-core to LTSV for the purposes of structured data visualization.

The new format has the following fields, separated by tabs:
* timestamp: a timestamp of when the log is made;
* created: the same timestamp in the unix epoch format;
* jobname: the name of the data job;
* level: the logging level - one of INFO, WARNING, DEBUG, ERROR;
* modulename: the name of the module, inside of which the logging call is made;
* filename: the name of the file containing the logging call being made;
* lineno: the number of the line of code, at which the logging call is made;
* funcname: the name of the function, inside which the loggin call is made;
* attemptid: string identifying this particular execution of the data job;
* message: any additional logged information.

The label names follow the labelling recommendations found at http://ltsv.org/.

After configuration, logs will be automatically formatted to LTSV format. They would start to look something like this:
```
@timestamp:2021-08-04T12:51:11	created:1628070671	jobname:example-job	level:DEBUG	modulename:vdk.internal.trino_connection	filename:managed_connection_base.py	lineno:69	funcname:connect	attemptid:1628070671-452613-739749	message:Established <trino.dbapi.Connection object at 0x10b9b1d30>
@timestamp:2021-08-04T12:51:11	created:1628070671	jobname:example-job	level:DEBUG	modulename:vdk.internal.trino_connection	filename:managed_cursor.py	lineno:29	funcname:execute	attemptid:1628070671-452613-739749	message:Executing query: select 1
```


# JSON

This is a POC level implementation of a plugin which changes the logging format of vdk-core to JSON for the purposes of structured data visualization in a log aggregator.

The new format has the following fields:
 * @timestamp: a timestamp of when the log is made;
 * jobname: the name of the data job;
 * level: the logging level - one of INFO, WARNING, DEBUG, ERROR;
 * modulename: the name of the module, inside of which the logging call is made;
 * filename: the name of the file containing the logging call being made;
 * lineno: the number of the line of code, at which the logging call is made;
 * funcname: the name of the function, inside which the loggin call is made;
 * attemptid: string identifying this particular execution of the data job;
 * message: any additional logged information.

If the log record contains an error, it will also contain the following fields:
 * error.message: the message of the exception;
 * error.stack_trace: a stack trace of the exception;
 * error.type: the type of exception.

The label names follow the labelling recommendations found at http://ltsv.org/.
The reason we chose the LTSV naming standard is due to the fact that this plugin was based on a previous LTSV-formatting plugin,
as well as the fact that there is no single JSON naming standard.

Additionally, double quote characters within the message are escaped.


After configuration all logs will be automatically formatted to JSON. They will appear like this:
```
{"@timestamp": "2021-10-14T11:37:44.703Z", "message": "Checking if job should be skipped:", "level": "INFO", "lineno": 102, "filename": "execution_skip.py", "modulename": "vdk.plugin.control_cli_plugin.execution_skip", "funcname": "_skip_job_if_necessary", "jobname": "gg-job4", "attemptid": "1634211464-1ee897-a3f0eb"}```
```

# Usage

Installing the plugin:

```python
pip install vdk-logging-format
```

After, configure the log format by setting the `LOGGING_FORMAT` configuration variable to `JSON` or `LTSV`.
