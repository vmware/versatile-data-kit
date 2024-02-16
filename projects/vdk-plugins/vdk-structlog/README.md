# Structured Logging For VDK

<a href="https://pypistats.org/packages/vdk-structlog" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-structlog.svg" alt="monthly download count for vdk-structlog"></a>

This plugin allows users to:
- select the log output format
- configure the logging metadata
- display metadata added by bound loggers
- emit logs to syslog

For a more in-depth technical analysis, check out [VEP-2448](https://github.com/vmware/versatile-data-kit/blob/main/specs/vep-2448-vdk-run-logs-simplified-and-readable/README.md)

## Usage

```
pip install vdk-structlog
```

### Configuration

(`vdk config-help` is a useful command to browse all config options of your installation of vdk)

| Name                          | Description                                                                                                                                                                                                                      | Example Value                                           | Possible Values                                                                                                                                                                                                                                                     |
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| use_structlog                 | Use the structlog logging config instead of using the one in vdk-core (True by default).                                                                                                                                         | "True"                                                  | "True", "False"                                                                                                                                                                                                                                                     |
| structlog_metadata            | Configure the metadata that will be output along with the log message                                                                                                                                                            | "timestamp, level, logger_name, file_name, vdk_job_name | Any combination of the following: "timestamp, level, logger_name, file_name, line_number, function_name, vdk_job_name, vdk_step_name, vdk_step_type". Can be expanded by extra params and bound key-value pairs. See the bound logger examples for more information |
| structlog_format              | Configure the logging output format. Available formats: json, console, ltsv                                                                                                                                                      | "console"                                               | "console", "json", "ltsv"                                                                                                                                                                                                                                           |
| structlog_console_log_pattern | Custom format string for console logging, applied only when`logging_format` is 'console'. Overrides `logging_metadata`. Note: For config.ini, %-signs should be escaped by doubling, e.g. %(asctime)s should become %%(asctime)s | "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"   | Any valid Python logging format string                                                                                                                                                                                                                              |
| structlog_config_preset       | Choose a configuration preset. Any config options set together with the preset will override the preset options. Available presets: LOCAL, CLOUD.                                                                                | "CLOUD"                                                 | "console", "json", "ltsv"                                                                                                                                                                                                                                           |
| structlog_format_init_logs    | Set to True to apply structlog formatting options to vdk initialization logs                                                                                                                                                     | "True"                                                  | "True", "False"                                                                                                                                                                                                                                                     |
| log_level_module              | Configure the log level of different Python modules separately                                                                                                                                                                   | "a.b.c=INFO;foo.bar=ERROR"                              | Semicolon-separated list of pairs of Python module paths and log level labels                                                                                                                                                                                       |
| syslog_host                   | Syslog host to which logs are emitted                                                                                                                                                                                            | "syslog.vmware.com"                                     | Any valid host name                                                                                                                                                                                                                                                 |
| syslog_port                   | Syslog port used to emit logs                                                                                                                                                                                                    | 514                                                     | Any valid port number                                                                                                                                                                                                                                               |
| syslog_protocol               | Protocol used to emit logs                                                                                                                                                                                                       | "UDP"                                                   | "TCP", "UDP"                                                                                                                                                                                                                                                        |
| syslog_enabled                | Enable/disable syslog                                                                                                                                                                                                            | "True"                                                  | "True", "False"                                                                                                                                                                                                                                                     |

### Example: Configure Custom Console Format

If you wish to apply a specific format to your console logs, you can define a
custom format using the `custom_console_log_pattern` configuration. This custom
format string will be used only when the `logging_format` is set to 'console'.

For example, add the following to your data job configuration:

```ini
[vdk]
custom_console_log_pattern=%(asctime)s %(name)-12s %(levelname)-8s %(message)s
```
When you run your data job, regardless of other logging settings, your logs will
strictly follow this custom format, displaying the timestamp, logger's name, log
level, and the log message as per the format string specified.

```log
2023-10-17 11:20:59,202 managed_cursor    INFO     ingest-from-db-example-job - Executing query SUCCEEDED. Query duration 00h:00m:00s
2023-10-17 11:20:59,202 managed_connectio INFO     ingest-from-db-example-job - Fetching query result...
2023-10-17 11:20:59,202 managed_cursor    INFO     ingest-from-db-example-job - Fetching all results from query ...
2023-10-17 11:20:59,202 managed_cursor    INFO     ingest-from-db-example-job - Fetching all results from query SUCCEEDED.
2023-10-17 11:20:59,202 managed_cursor    INFO     ingest-from-db-example-job - Closing DB cursor ...
2023-10-17 11:20:59,202 managed_cursor    INFO     ingest-from-db-example-job - Closing DB cursor SUCCEEDED.
2023-10-17 11:20:59,203 file_based_step   INFO     ingest-from-db-example-job - Entering 30_ingest_to_table.py#run(...) ...
2023-10-17 11:20:59,203 ingester_router   INFO     ingest-from-db-example-job - Sending tabular data for ingestion with method: sqlite and target: None
2023-10-17 11:20:59,204 file_based_step   INFO     ingest-from-db-example-job - Exiting  30_ingest_to_table.py#run(...) SUCCESS
```


### Example: Configure metadata

Create a data job and add the following config options

```ini
[vdk]
logging_metadata=timestamp,level,file_name,vdk_job_name
logging_format=console
```

Then run the data job. You should see just the configured tags where relevant.
For example, you won't see the vdk_job_name outside of log statements directly
related to job execution.

```log
2023-10-17 11:20:59,202 [VDK] [INFO ]    managed_cursor.py ingest-from-db-example-job - Executing query SUCCEEDED. Query duration 00h:00m:00s
2023-10-17 11:20:59,202 [VDK] [INFO ] managed_connection_b ingest-from-db-example-job - Fetching query result...
2023-10-17 11:20:59,202 [VDK] [INFO ]    managed_cursor.py ingest-from-db-example-job - Fetching all results from query ...
2023-10-17 11:20:59,202 [VDK] [INFO ]    managed_cursor.py ingest-from-db-example-job - Fetching all results from query SUCCEEDED.
2023-10-17 11:20:59,202 [VDK] [INFO ]    managed_cursor.py ingest-from-db-example-job - Closing DB cursor ...
2023-10-17 11:20:59,202 [VDK] [INFO ]    managed_cursor.py ingest-from-db-example-job - Closing DB cursor SUCCEEDED.
2023-10-17 11:20:59,203 [VDK] [INFO ]   file_based_step.py ingest-from-db-example-job - Entering 30_ingest_to_table.py#run(...) ...
2023-10-17 11:20:59,203 [VDK] [INFO ]   ingester_router.py ingest-from-db-example-job - Sending tabular data for ingestion with method: sqlite and target: None
2023-10-17 11:20:59,204 [VDK] [INFO ]   file_based_step.py ingest-from-db-example-job - Exiting  30_ingest_to_table.py#run(...) SUCCESS
```

Now, let's remove the timestamp from the configuration and add the line number

```ini
[vdk]
logging_metadata=level,file_name,line_number,vdk_job_name
logging_format=console
```

And run the job again

```log
[INFO ]    managed_cursor.py :97   ingest-from-db-example-job - Executing query SUCCEEDED. Query duration 00h:00m:00s
[INFO ] managed_connection_b :133  ingest-from-db-example-job - Fetching query result...
[INFO ]    managed_cursor.py :193  ingest-from-db-example-job - Fetching all results from query ...
[INFO ]    managed_cursor.py :196  ingest-from-db-example-job - Fetching all results from query SUCCEEDED.
[INFO ]    managed_cursor.py :203  ingest-from-db-example-job - Closing DB cursor ...
[INFO ]    managed_cursor.py :205  ingest-from-db-example-job - Closing DB cursor SUCCEEDED.
[INFO ]   file_based_step.py :103  ingest-from-db-example-job - Entering 30_ingest_to_table.py#run(...) ...
[INFO ]   ingester_router.py :106  ingest-from-db-example-job - Sending tabular data for ingestion with method: sqlite and target: None
[INFO ]   file_based_step.py :109  ingest-from-db-example-job - Exiting  30_ingest_to_table.py#run(...) SUCCESS
```

### Example: Configure logging format

Create a data job and add the following config options

```ini
[vdk]
logging_metadata=timestamp,level,file_name,vdk_job_name
logging_format=json
```

And you should see json-formatted logs.

```
{"filename": "managed_cursor.py", "lineno": 97, "vdk_job_name": "ingest-from-db-example-job", "message": "Executing query SUCCEEDED. Query duration 00h:00m:00s", "vdk_step_name": "20_create_table.sql", "vdk_step_type": "sql", "timestamp": 1697532608.968082, "level": "INFO"}
{"filename": "managed_connection_base.py", "lineno": 133, "vdk_job_name": "ingest-from-db-example-job", "message": "Fetching query result...", "vdk_step_name": "20_create_table.sql", "vdk_step_type": "sql", "timestamp": 1697532608.9681149, "level": "INFO"}
{"filename": "managed_cursor.py", "lineno": 193, "vdk_job_name": "ingest-from-db-example-job", "message": "Fetching all results from query ...", "vdk_step_name": "20_create_table.sql", "vdk_step_type": "sql", "timestamp": 1697532608.968137, "level": "INFO"}
{"filename": "managed_cursor.py", "lineno": 196, "vdk_job_name": "ingest-from-db-example-job", "message": "Fetching all results from query SUCCEEDED.", "vdk_step_name": "20_create_table.sql", "vdk_step_type": "sql", "timestamp": 1697532608.9681568, "level": "INFO"}
{"filename": "managed_cursor.py", "lineno": 203, "vdk_job_name": "ingest-from-db-example-job", "message": "Closing DB cursor ...", "vdk_step_name": "20_create_table.sql", "vdk_step_type": "sql", "timestamp": 1697532608.968405, "level": "INFO"}
{"filename": "managed_cursor.py", "lineno": 205, "vdk_job_name": "ingest-from-db-example-job", "message": "Closing DB cursor SUCCEEDED.", "vdk_step_name": "20_create_table.sql", "vdk_step_type": "sql", "timestamp": 1697532608.9684658, "level": "INFO"}
{"filename": "file_based_step.py", "lineno": 103, "vdk_job_name": "ingest-from-db-example-job", "message": "Entering 30_ingest_to_table.py#run(...) ...", "vdk_step_name": "30_ingest_to_table.py", "vdk_step_type": "python", "timestamp": 1697532608.9734771, "level": "INFO"}
{"filename": "ingester_router.py", "lineno": 106, "vdk_job_name": "ingest-from-db-example-job", "message": "Sending tabular data for ingestion with method: sqlite and target: None", "vdk_step_name": "30_ingest_to_table.py", "vdk_step_type": "python", "timestamp": 1697532608.975029, "level": "INFO"}
{"filename": "file_based_step.py", "lineno": 109, "vdk_job_name": "ingest-from-db-example-job", "message": "Exiting  30_ingest_to_table.py#run(...) SUCCESS", "vdk_step_name": "30_ingest_to_table.py", "vdk_step_type": "python", "timestamp": 1697532608.976068, "level": "INFO"}
```

### Example: Bound loggers

Python's logging module allows you to pass extra params as a dict. vdk-structlog
takes this into account and displays the extra params, as long as they're added
to `structlog_metadata` in config.ini

```python
import logging
import uuid

log = logging.getLogger(__name__)

myid = uuid.uuid4()
log.info(f"Starting job step {__name__}")
log.info("This is an info log statement with extra stuff.", extra={"uuid": myid})
```

```ini
[vdk]
structlog_metadata=timestamp,level,logger_name,file_name,line_number,function_name,uuid
structlog_format=console
```

```log
2024-01-16 10:16:53,237 [VDK] [INFO ] step_20_python_ste                20_python_step.py :21   run               - Starting job step step_20_python_ste
2024-01-16 10:16:53,237 [VDK] [INFO ] step_20_python_ste                20_python_step.py :22   run              78118954-fe0c-451d-80cf-9b9bc80b8140 - This is an info log statement with extra stuff
```

This is fine, however, if we want to have the same uuid with multiple log
statements, it's not very convenient to pass it every time. `vdk` offers a
function to solve this problem.

```python
import logging
import uuid
from vdk.internal.core.logging import bind_logger

log = logging.getLogger(__name__)

log.info(f"Starting job step {__name__}")

myid = uuid.uuid4()
bound_log = bind_logger(log, {"uuid": myid})
bound_log.info("This is an info log statement with extra stuff")
bound_log.info("This is another log statement with uuid")
```

```ini
[vdk]
structlog_metadata=timestamp,level,logger_name,file_name,line_number,function_name,uuid
structlog_format=console
```

Now every time you log using the bound logger, you have the uuid attached.

```log
2024-01-16 10:31:04,761 [VDK] [INFO ] step_20_python_ste                20_python_step.py :22   run               - Starting job step step_20_python_ste
2024-01-16 10:31:04,761 [VDK] [INFO ] step_20_python_ste                20_python_step.py :25   run              ed1e447d-3746-4068-8a83-353176327985 - This is an info log statement with extra stuff
2024-01-16 10:31:04,761 [VDK] [INFO ] step_20_python_ste                20_python_step.py :26   run              ed1e447d-3746-4068-8a83-353176327985 - This is another log statement with uuid
```

Bound loggers act the same as regular loggers. You can even pass extra params to
them, or bind additional context.

```python
import logging
import uuid
from vdk.internal.core.logging import bind_logger

log = logging.getLogger(__name__)

log.info(f"Starting job step {__name__}")

myid = uuid.uuid4()
bound_log = bind_logger(log, {"uuid": myid})
bound_log.info("This is an info log statement with extra stuff")
bound_log.info("This is another log statement with uuid")
bound_log.info("More stuff", extra={"new_key": "new_value", "extra_key":"more_value"})
rebound_log = bind_logger(bound_log, {"another_key": "another_value"})
```

```ini
[vdk]
structlog_metadata=timestamp,level,logger_name,file_name,line_number,function_name,uuid,new_key,another_key,extra_key
structlog_format=console
```

### Syslog support

Outputting logs to a syslog server is supported with the following config
options

```ini
[vdk]
syslog_host=localhost
syslog_port=514
syslog_protocol=UDP
syslog_enabled=True
```

The syslog output format is set to `console` and the following formatter string
is used. These are currently not configurable.

```python
DETAILED_FORMAT =
    "%(asctime)s [VDK] %(job_name)s [%(levelname)-5.5s] %(name)-30.30s %(filename)20.20s:%("
    "lineno)-4.4s %(funcName)-16.16s[id:%(attempt_id)s]- %(message)s"
```

### Build and test

```
pip install -r requirements.txt
pip install -e .
pytest
```

The
[../build-plugin.sh](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/build-plugin.sh)
script can be used also.


#### Note about the CICD:

.plugin-ci.yaml is needed only for plugins part of [Versatile Data Kit Plugin repo](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins).

The CI/CD is separated in two stages, a build stage and a release stage. The
build stage is made up of a few jobs, all which inherit from the same job
configuration and only differ in the Python version they use (3.7, 3.8, 3.9 and
3.10). They run according to rules, which are ordered in a way such that changes
to a plugin's directory trigger the plugin CI, but changes to a different plugin
does not.
