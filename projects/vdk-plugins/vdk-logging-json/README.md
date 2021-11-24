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

# Usage

Switching vdk logging can be done by simply installing the plugin:

```python
pip install vdk-logging-json
```

And all logs will be automatically formatted to JSON. They will appear like this:
```
{"@timestamp": "2021-10-14T11:37:44.703Z", "message": "Checking if job should be skipped:", "level": "INFO", "lineno": 102, "filename": "execution_skip.py", "modulename": "vdk.plugin.control_cli_plugin.execution_skip", "funcname": "_skip_job_if_necessary", "jobname": "gg-job4", "attemptid": "1634211464-1ee897-a3f0eb"}```
