# Structured Logging For VDK

This plugin allows users to:
- select the log output format
- configure the logging metadata
- display metadata added by bound loggers

## Usage

```
pip install vdk-structlog
```

### Configuration

(`vdk config-help` is useful command to browse all config options of your installation of vdk)

| Name                       | Description                                                                                                               | Example Value                                           | Possible Values                                                                                                    |
|----------------------------|---------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| logging_metadata           | Configure the metadata that will be output along with the log message                                                     | "timestamp, level, logger_name, file_name, vdk_job_name | "timestamp, level, logger_name, file_name, line_number, function_name, vdk_job_name, vdk_step_name, vdk_step_type" |
| logging_format             | Configure the logging output format. Available formats: json, console                                                     | "console"                                               | "console", "json"                                                                                                  |
| custom_console_log_pattern | Custom format string for console logging, applied only when`logging_format` is 'console' and overrides `logging_metadata` | "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"   | Any valid Python logging format string                                                                             |

### Example: Configure Custom Console Format

If you wish to apply a specific format to your console logs, you can define a custom format using the `custom_console_log_pattern` configuration. This custom format string will be used only when the `logging_format` is set to 'console'.

For example, add the following to your data job configuration:

```
[vdk]
custom_console_log_pattern=%(asctime)s %(name)-12s %(levelname)-8s %(message)s
```
When you run your data job, regardless of other logging settings, your logs will strictly follow this custom format, displaying the timestamp, logger's name, log level, and the log message as per the format string specified.

```
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

```
[vdk]
logging_metadata=timestamp,level,file_name,vdk_job_name
logging_format=console
```

Then run the data job. You should see just the configured tags where relevant.
For example, you won't see the vdk_job_name outside of log statements directly
related to job execution.

 ```
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

```
logging_metadata=level,file_name,line_number,vdk_job_name
logging_format=console
```

And run the job again

```
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

```
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

TODO: Add an example once bound loggers are part of vdk-core

### Example: Passing custom metadata fields with extra_params

TODO: Add an example

### Build and test

```
pip install -r requirements.txt
pip install -e .
pytest
```

In VDK repo [../build-plugin.sh](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/build-plugin.sh) script can be used also.


#### Note about the CICD:

.plugin-ci.yaml is needed only for plugins part of [Versatile Data Kit Plugin repo](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins).

The CI/CD is separated in two stages, a build stage and a release stage.
The build stage is made up of a few jobs, all which inherit from the same
job configuration and only differ in the Python version they use (3.7, 3.8, 3.9 and 3.10).
They run according to rules, which are ordered in a way such that changes to a
plugin's directory trigger the plugin CI, but changes to a different plugin does not.
