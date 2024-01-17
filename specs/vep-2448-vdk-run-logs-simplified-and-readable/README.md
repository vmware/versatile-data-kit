
# VEP-2448: VDK Run Logs: Simplified And Readable

* **Author(s):** Dilyan Marinov (mdilyan@vmware.com), Antoni Ivanov (aivanov@vmware.com)
<!-- * **Status:** draft | implementable | implemented | rejected | withdrawn | replaced -->
* **Status:** draft

<!-- Provide table of content as it's helpful. -->

- [VEP-2448: VDK Run Logs: Simplified And Readable](#vep-2448-vdk-run-logs-simplified-and-readable)
  - [Summary](#summary)
  - [Glossary](#glossary)
  - [Motivation](#motivation)
    - [Logs on failures](#logs-on-failures)
    - [Logs on success](#logs-on-success)
    - [Debug mode](#debug-mode)
    - [Progress Tracking](#progress-tracking)
    - [VDK exception handling and categorization](#vdk-exception-handling-and-categorization)
  - [Requirements and goals](#requirements-and-goals)
  - [High-level design](#high-level-design)
    - [Log Structure](#log-structure)
      - [Resources](#resources)
    - [Log Less](#log-less)
      - [Logs not at the apprpopriate level](#logs-not-at-the-apprpopriate-level)
    - [Clean Error Handling](#clean-error-handling)
    - [Progress Indicators](#progress-indicators)
  - [Detailed design](#detailed-design)
    - [Log Structure](#log-structure-1)
    - [Log Less](#log-less-1)
    - [Clean Error Handling](#clean-error-handling-1)
    - [Progress Indicators](#progress-indicators-1)
      - [Technical Requirements](#technical-requirements)
        - [Core Components](#core-components)
          - [ProgressTracker](#progresstracker)
          - [API Methods](#api-methods)
          - [ProgressPresenter](#progresspresenter)
          - [Workflow](#workflow)
          - [vdk-tqdm plugin](#vdk-tqdm-plugin)
        - [Pseudo code](#pseudo-code)
  - [Implementation stories](#implementation-stories)
    - [Log Structure - In Progress](#log-structure---in-progress)
    - [Log Less - Completed](#log-less---completed)
    - [Clean Error Handling - Completed](#clean-error-handling---completed)
    - [Progress Indicators - De-scoped](#progress-indicators---de-scoped)
      - [Implement ProgressTracker in vdk-core](#implement-progresstracker-in-vdk-core)
      - [Create Child Tracker for New Steps](#create-child-tracker-for-new-steps)
      - [Add SQL Query Support](#add-sql-query-support)
      - [Track DAG Job Progress](#track-dag-job-progress)
      - [Ingestion Tracker](#ingestion-tracker)
      - [Implement Basic Logging Strategy](#implement-basic-logging-strategy)
      - [CLI Progress with TQDM Plugin](#cli-progress-with-tqdm-plugin)
      - [TQDM Support in Notebooks](#tqdm-support-in-notebooks)
      - [Configurable Tracking Strategy and configureable tracker](#configurable-tracking-strategy-and-configureable-tracker)
    - [Documentation](#documentation)
    - [Promotional Materials](#promotional-materials)
  - [Alternatives](#alternatives)
    - [Progress trackers 3th party libraries research](#progress-trackers-3th-party-libraries-research)

## Summary

<!--
Short summary of the proposal. It will be used as user-focused
documentation such as release notes or a (customer facing) development roadmap.
The tone and content of the `Summary` section should be
useful for a wide audience.
-->

<!-- TODO: Revisit this section once the all other sections are completed -->
The VDK user experience when it comes to using logs for data job runs is lacking
in several areas. This makes it hard to debug failed data job runs and get
useful information out of successful data job runs. The following sections
provide an in-depth view of improvemnts to VDK run logs which address a number
of user pain points, such as noisy logs, overly verbose error messages,
insufficient error information, lack of documentation, lack of progress tracking
features, etc. Resolving these pain points will result in a better user
experience.

## Glossary
<!--
Optional section which defines terms and abbreviations used in the rest of the document.
-->

## Motivation
<!--
It tells **why** do we need X?
Describe why the change is important and the benefits to users.
Explain the user problem that need to be solved.
-->

VKD users face multiple challenges related to logging in data job runs. Based on
user feedback, these can be split into 5 categories.

### Logs on failures

Relevant troubleshooting or user-added information gets lost in the noise.
Sometimes it's just missing. Some error messages contain generic statements. We
have incentivized bad practices with our error message format. They have the
characteristics of a form, so developers sometimes write placeholder text, e.g.
"WHAT HAPPENED: An error occurred", or "COUNTERMEASURES: Check exception".
Generic messages are extremely annoying from an user perspective. When a step
fails, we don't point to the actual line of the code where the failure happened.
Root causes are sometimes buried in the stack trace. There's lots of meta-logs,
query logs, etc. This suggest there is a lot of info logging that should
actually be on the debug level.

### Logs on success

Users expect little or no log output on success. They sometimes add logs to
signify when a step started or ended. Users these kinds of logs to be easily
discoverable in the output.

### Debug mode

Some users have trouble running jobs in debug mode and getting debug level logs
This points to a gap in our documentation

### Progress Tracking

Tracking of job progress (for DAGs, steps, ingestion) should be improved. Right
now it's not easy to differentiate between logs for parent jobs, child jobs and
jobs running in parallel when it comes to dags. It's also not easy to see how
much data was ingested or get data about resource consumption while the job is
still running.

### VDK exception handling and categorization

Troubleshooting from existing log output is not straightforward. It is hard to
find the exact line where the error occurred. Sometimes the actual exception is
buried in the log output, or wrapped in another exception and obscured. Error
categorisation is very limited, e.g. the user knows there's a platform error, in
the ingestion module, but the exact type of error is unknown. More granular
categorization would help cloud teams troubleshoot errors fasters. Inside data
jobs, it is not straightforward to handle exceptions comping from libraries
(e.g. pandas), because they get wrapped in vdk errors.

## Requirements and goals
<!--
It tells **what** is it trying to achieve?
List the specific goals (functional and nonfunctional requirements)? How will we
know that this has succeeded?

Specify non-goals. Clearly, the list of non-goals can't be exhaustive.
Non-goals are only features, which a contributor can reasonably assume were a goal.
One example is features that were cut during scoping.
-->

1. Troubleshooting failed data job runs from stack traces is straightforward
   1. Stack traces are easy to navigate
   2. Stack traces are not printed multiple times
   4. Stack traces do not contain generic messages like "An exception occurred"
   3. Additional information in logs is configurable, e.g. job summary
   4. Non-vdk exceptions can be handled inside data jobs
   5. All log statements are at the appropriate level
   6. Changing the logging level per module is documented
2. Successful data job runs contain the appropriate amount of information
   1. Logs for successful runs should not be verbose
   2. User log statements should be easy to find within success logs
3. Adding and removing metadata information is easy. Users are able to
   1. Add/remove the vdk job name
   2. Add/remove the vdk step name
   3. Add/remove any of the built-in logging metadata, e.g. timestamp, filename
   4. Add/remove custom metadata fields
   5. Select custom loggin formats
4. Syslog is supported
5. Users can have progress indicators instead of logs
   1. Users can switch progress indicators on and off
   2. Progress indicators show the amount of ingested data
   3. Progress indicators show the amount of resources currently consumed
   1. Progress indicators show current job name (this should also be supported in regular logs)
   1. Progress indicators show parent job name, in the case of DAGs (this should also be supported in regular logs)
   1. DAG jobs that run in parallel can be sorted and grouped, so that progress bars or logs for a single job are visible
6. The above points are valid for local and cloud data job runs.

**Out of scope**

Issues related to VDK internal cloud deployments, e.g. write permissions, data
format issues, etc. These should be forwarded to the appropriate VMWare team.


## High-level design

<!--
All the rest sections tell **how** are we solving it?

This is where we get down to the specifics of what the proposal actually is.
This should have enough detail that reviewers can understand exactly what
you're proposing, but should not include things like API designs or
implementation. What is the desired outcome and how do we measure success?

Provide a valid UML Component diagram that focuses on the architecture changes
implementing the feature. For more details on how to write UML Component Spec -
see https://en.wikipedia.org/wiki/Component_diagram#External_links.

For every new component on the diagram, explain which goals does it solve.
In this context, a component is any separate software process.

-->

Based on user feedback, we've identified 4 workstreams.

### Log Structure

```
2023-07-27 17:50:44,918 [VDK] hackernews-top-stories [INFO ] vdk.plugin.control_cli_plugin. properties_plugin.py:30   initialize_job  [id:30618c1b-677b-4f96-86a3-dda26011b3d8-1690469444-20a99]- Control Service REST API URL is not configured. Will not initialize Control Service based Properties client implementation.
```

`[Local][Cloud]` The current logging format is static and looks something like `<timestamp> [VDK] <job-name> <level> <plugin:line> <step> <id> <message>`. We need a way to configure
this format dynamically on the data job and on the environment level.

Key ideas to implement:

- expose the logging format as an env variable that's overridable per job
- provide configuration for users to specify the metadata they want logged, e.g.
  pass a config like `timestamp, level` to display just the timestamp and level
  and not the filename, etc..
- provide configuration for users to pass their own metadata, e.g. a user should
  be able to pass a metadata parameter like `my_special_param=my_special_value`
  to a log statement, then edit config.ini so it's displayed for all log
  statements where it's available
- support different formats, e.g. console, json, ltsv, key-value

#### Resources

**Handlers**
https://docs.python.org/3/library/logging.html#handler-objects
https://docs.python.org/3/howto/logging-cookbook.html#imparting-contextual-information-in-handlers

**Filters**
https://docs.python.org/3/library/logging.html#filter-objects

**LogRecords**

https://docs.python.org/3/library/logging.html#logrecord-objects

**Additional reading**

https://docs.python.org/3/howto/logging.html
https://realpython.com/python-logging/
https://realpython.com/python-logging-source-code/

**Logging adapters a.k.a. bound loggers**
https://docs.python.org/3/howto/logging-cookbook.html#context-info

Example:

```python
class BoundLogger(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        # merge bound extra dict with existing extra dict if any
        if "extra" in kwargs:
            kwargs["extra"] = {**self.extra, **kwargs["extra"]}
        else:
            kwargs["extra"] = self.extra
        return msg, kwargs


log = logging.getLogger(__name__)
bound = BoundLogger(log, {"bound_key": "bound_value"})
bound.warning("From vdk_initialize", extra={"first": "first_value", "second": "second_value"})
bound.warning("Something else from vdk_initialize")
```

### Log Less

#### Logs not at the apprpopriate level

`[Local][Cloud]` Every log statement is audited and the logging level changed if
necessary. Redundant logging is removed entirely. Judging by user feedback, we
have a lot of INFO logging that should be at the DEBUG level.

`[Local][Cloud]` There is an easy way to for the user configure the datajob log
level dynamically.

Note: There is currently log_level_module which you can set to
a.b.c=INFO;foo.bar=ERROR. We have to decide if this level of granularity is
sufficient. We should also improve the documentation around it.

### Clean Error Handling

`[Local][Cloud]` Remove the log-and-throw and log-and-rethrow patterns. Errors
are passed up the call stack to the original caller. Errors are caught and
wrapped or replaced by other errors only if we're adding more information to the
existing error. There is a single exit point for error handling to avoid loggin
exceptions and passing them up the call stack.

`[Local][Cloud]` The current error handling mechanism is coupled with logging.
This has encouraged bad practices, such as making the caller add irrelevant
information, e.g.

```
"WHAT HAPPENED: An error occurred",
"COUNTERMEASURES: Check exception"
```

We don't provide sufficient granularity in the errors that can be thrown and
rely on the caller to "do the right thing", in this case, add relevant
information. Error classification is modified to use a class hierarchy of errors
which help classify the problem without making the caller pass all the relevant
information every time.

### Progress Indicators

`[Local]` Replace logs with progress indicators entirely. Give the user the
option to choose between progress indicators and logs for local jobs.

Progress indicators work on multiple levels. Therefore, they should have their
own plugin There are three levels of tracking
- DAGs
- Jobs
- Job Steps

Additonally, we could consider a fourth level - users tracking progress inside
data jobs steps, e.g. percentage of data ingested. This would require exposing
an API for the users.

`[Cloud]` A progress tracking plugin is useful for cloud deployments as well.
Cloud jobs will not use progress bars, but could still use the plugin tracking
system to display logs instead.

`[Local]` Logs on failure point directly to the problem and provide the minimum
amount of troubleshooting information to get started. Error messages in the
console show the root cause and the line where the error happened. Full error
log is available in a separate file.

```
process_twitter_data Step 10_ingest_data.py Line: 38
File with path "./some_file.txt does not exist
Full error log /tmp/30618c1b-677b-4f96-86a3-dda26011b3d8-1690469444-20a99/error.log
```

`[Cloud]` Full error log is output to stderr

Resources:

- https://pypi.org/project/progress2/
- https://tqdm.github.io/
- https://joblib.readthedocs.io/en/stable/

## Detailed design

### Log Structure

All logging configuration is in a separate plugin `vdk-structlog`. Default
logging configuration is still available in `vdk-core`, but it's overridden by
`vdk-structlog`.

**Metadata config**

Users are able to override the default logging format structure so that metadata
fields they don't care about are hidden. This is available through standard vdk
configuration, e.g. config.ini or env variables. Operators can pass the same
kind of config when deploying control service.

```ini
[vdk]
structlog_metadata=timestamp,level,logger_name,file_name,line_number,function_name
structlog_format=console
```

Note: Two additional metadata fields are available out of the box -
`vdk_job_name` and `vdk_step_name`. They are not added in the examples for
brevity.

Users can pass a custom format string with %-formatting and are not forced to
use pre-configured metadata fields at all cost. This format string is valid only
for the console format.

```python
structlog_console_custom_format=%(asctime)s [VDK] %(job_name)s [%(levelname)-5.5s] %(name)-30.30s %(filename)20.20s:%(lineno)-4.4s %(funcName)-16.16s[id:%(attempt_id)s]- %(message)s
```

**Log formatting**

Users are able to choose between different log output formats by passing a
config option. The formats initially supported are `console`, `json` and
`ltsv`. The pre-configured metadata fields are usable with all formats.

```ini
[vdk]
structlog_logging_format=console
```

Output
```log
2024-01-16 10:51:55,058 [VDK] [INFO ] vdk.internal.cli_entry                 cli_entry.py :135  vdk_main           - Start CLI vdk with args ['run', '.']
2024-01-16 10:51:55,074 [VDK] [INFO ] vdk.internal.builtin_plugins.r           cli_run.py :228  run                - Versatile Data Kit (VDK)
Version: 0.3.1134532671
Build details: RELEASE_VERSION=0.3.1134532671, BUILD_DATE=Thu Jan 11 10:09:08 UTC 2024, BUILD_MACHINE_INFO=Linux runner-xumbkon8-project-28359933-concurrent-0krnrr 5.4.235-144.344.amzn2.x86_64 #1 SMP Sun Mar 12 12:50:22 UTC 2023 x86_64 GNU/Linux, GITLAB_CI_JOB_ID=5908208720, GIT_COMMIT_SHA=16c6a2fc25ed811f65637f5f215a173ad45d9d6c, GIT_BRANCH=main
Python version: 3.11.7 64bit (/opt/homebrew/opt/python@3.11/bin/python3.11)

Installed plugins:
vdk-sqlite (from package vdk-sqlite, version 0.1.954571638)
vdk-server (from package vdk-server, version 0.1.948436673)
vdk-structlog (from package vdk-structlog, version 0.1.1133681733)
vdk-logging-format (from package vdk-logging-format, version 0.1.1070203945)
vdk-control-service-properties (from package vdk-plugin-control-cli, version 0.1.948436673)
vdk-execution-skip (from package vdk-plugin-control-cli, version 0.1.948436673)
vdk-plugin-control-cli (from package vdk-plugin-control-cli, version 0.1.948436673)
vdk-ingest-file (from package vdk-ingest-file, version 0.1.948436673)
vdk-ingest-http (from package vdk-ingest-http, version 0.2.948436673)
--------------------------------------------------------------------------------
2024-01-16 10:51:55,074 [VDK] [INFO ] vdk.internal.builtin_plugins.r           cli_run.py :150  create_and_run_d   - Run job with directory /Users/mdilyan/Projects/vdk-playground/hello-world
2024-01-16 10:51:55,080 [VDK] hello-world [INFO ] vdk.plugin.control_cli_plugin. properties_plugin.py:30   initialize_job  [id:d9064de6-710c-4006-bc7b-686e39e3c305-1705395115-673db]- Control Service REST API URL is not configured. Will not initialize Control Service based Properties client implementation.
2024-01-16 10:51:55,080 [VDK] [INFO ] vdk.plugin.control_cli_plugin.    execution_skip.py :105  _skip_job_if_nec   - Checking if job should be skipped:
2024-01-16 10:51:55,080 [VDK] [INFO ] vdk.plugin.control_cli_plugin.    execution_skip.py :106  _skip_job_if_nec   - Job : hello-world, Team : my-team, Log config: LOCAL, execution_id: d9064de6-710c-4006-bc7b-686e39e3c305-1705395115
2024-01-16 10:51:55,080 [VDK] [INFO ] root                              execution_skip.py :111  _skip_job_if_nec   - Local execution, skipping parallel execution check.
2024-01-16 10:51:55,081 [VDK] [INFO ] vdk.plugin.sqlite.sqlite_conne sqlite_connection.py :29   new_connection     - Creating new connection against local file database located at: /var/folders/5d/bbd89v315777n_d24q2wznlh0000gr/T/vdk-sqlite.db
2024-01-16 10:51:55,082 [VDK] [INFO ] vdk.plugin.sqlite.sqlite_conne sqlite_connection.py :29   new_connection     - Creating new connection against local file database located at: /var/folders/5d/bbd89v315777n_d24q2wznlh0000gr/T/vdk-sqlite.db
2024-01-16 10:51:55,082 [VDK] [INFO ] vdk.internal.builtin_plugins.c    managed_cursor.py :170  _execute_operati   - Executing query:
-- job_name: hello-world
-- op_id: d9064de6-710c-4006-bc7b-686e39e3c305-1705395115
-- SQL scripts are standard SQL scripts. They are executed against Platform OLAP database.
-- Refer to platform documentation for more information.

-- Common uses of SQL steps are:
--    aggregating data from other tables to a new one
--    creating a table or a view that is needed for the python steps

-- Queries in .sql files can be parametrised.
-- A valid query parameter looks like → {parameter}.
-- Parameters will be automatically replaced if there is a corresponding value existing in the IJobInput properties.

CREATE TABLE IF NOT EXISTS hello_world (id NVARCHAR);

2024-01-16 10:51:55,082 [VDK] [INFO ] vdk.internal.builtin_plugins.c    managed_cursor.py :97   execute            - Executing query SUCCEEDED. Query duration 00h:00m:00s
2024-01-16 10:51:55,082 [VDK] [INFO ] vdk.internal.builtin_plugins.c managed_connection_b :133  execute_query      - Fetching query result...
2024-01-16 10:51:55,082 [VDK] [INFO ] vdk.internal.builtin_plugins.c    managed_cursor.py :187  fetchall           - Fetching all results from query ...
2024-01-16 10:51:55,082 [VDK] [INFO ] vdk.internal.builtin_plugins.c    managed_cursor.py :190  fetchall           - Fetching all results from query SUCCEEDED.
2024-01-16 10:51:55,082 [VDK] [INFO ] vdk.internal.builtin_plugins.c    managed_cursor.py :197  close              - Closing DB cursor ...
2024-01-16 10:51:55,082 [VDK] [INFO ] vdk.internal.builtin_plugins.c    managed_cursor.py :199  close              - Closing DB cursor SUCCEEDED.
2024-01-16 10:51:55,084 [VDK] [INFO ] vdk.internal.builtin_plugins.r   file_based_step.py :105  run_python_step    - Entering 20_python_step.py#run(...) ...
2024-01-16 10:51:55,084 [VDK] [INFO ] step_20_python_ste                20_python_step.py :22   run                - Starting job step step_20_python_ste
2024-01-16 10:51:55,084 [VDK] [INFO ] vdk.internal.builtin_plugins.i   ingester_router.py :64   send_object_for_   - Sending object for ingestion with method: sqlite and target: None
2024-01-16 10:51:55,085 [VDK] [INFO ] vdk.internal.builtin_plugins.r   file_based_step.py :111  run_python_step    - Exiting  20_python_step.py#run(...) SUCCESS
2024-01-16 10:51:57,091 [VDK] [INFO ] vdk.plugin.sqlite.ingest_to_sq  ingest_to_sqlite.py :76   ingest_payload     - Ingesting payloads for target: /var/folders/5d/bbd89v315777n_d24q2wznlh0000gr/T/vdk-sqlite.db; collection_id: hello-world|d9064de6-710c-4006-bc7b-686e39e3c305-1705395115
2024-01-16 10:51:57,092 [VDK] [INFO ] vdk.plugin.sqlite.sqlite_conne sqlite_connection.py :29   new_connection     - Creating new connection against local file database located at: /var/folders/5d/bbd89v315777n_d24q2wznlh0000gr/T/vdk-sqlite.db
2024-01-16 10:51:57,099 [VDK] [INFO ] vdk.internal.builtin_plugins.i     ingester_base.py :564  close_now          - Ingester statistics:
		Successful uploads: 1
		Failed uploads: 0
		Ingesting plugin errors: None

2024-01-16 10:51:57,099 [VDK] [INFO ] vdk.internal.builtin_plugins.r           cli_run.py :169  create_and_run_d   - Job execution result: SUCCESS
```

```ini
[vdk]
structlog_logging_format=json
```

Output
```json
{"name": "vdk.internal.cli_entry", "filename": "cli_entry.py", "lineno": 135, "funcName": "vdk_main", "message": "Start CLI vdk with args ['run', '.']", "level": "INFO", "timestamp": 1705395355.923014}
{"name": "vdk.internal.builtin_plugins.run.cli_run", "filename": "cli_run.py", "lineno": 228, "funcName": "run", "message": "Versatile Data Kit (VDK)\nVersion: 0.3.1134532671\nBuild details: RELEASE_VERSION=0.3.1134532671, BUILD_DATE=Thu Jan 11 10:09:08 UTC 2024, BUILD_MACHINE_INFO=Linux runner-xumbkon8-project-28359933-concurrent-0krnrr 5.4.235-144.344.amzn2.x86_64 #1 SMP Sun Mar 12 12:50:22 UTC 2023 x86_64 GNU/Linux, GITLAB_CI_JOB_ID=5908208720, GIT_COMMIT_SHA=16c6a2fc25ed811f65637f5f215a173ad45d9d6c, GIT_BRANCH=main\nPython version: 3.11.7 64bit (/opt/homebrew/opt/python@3.11/bin/python3.11)\n\nInstalled plugins:\nvdk-sqlite (from package vdk-sqlite, version 0.1.954571638)\nvdk-server (from package vdk-server, version 0.1.948436673)\nvdk-structlog (from package vdk-structlog, version 0.1.1133681733)\nvdk-logging-format (from package vdk-logging-format, version 0.1.1070203945)\nvdk-control-service-properties (from package vdk-plugin-control-cli, version 0.1.948436673)\nvdk-execution-skip (from package vdk-plugin-control-cli, version 0.1.948436673)\nvdk-plugin-control-cli (from package vdk-plugin-control-cli, version 0.1.948436673)\nvdk-ingest-file (from package vdk-ingest-file, version 0.1.948436673)\nvdk-ingest-http (from package vdk-ingest-http, version 0.2.948436673)\n--------------------------------------------------------------------------------", "level": "INFO", "timestamp": 1705395355.950686}
{"name": "vdk.internal.builtin_plugins.run.cli_run", "filename": "cli_run.py", "lineno": 150, "funcName": "create_and_run_data_job", "message": "Run job with directory /Users/mdilyan/Projects/vdk-playground/hello-world", "level": "INFO", "timestamp": 1705395355.9508228}
2024-01-16 10:55:55,956 [VDK] hello-world [INFO ] vdk.plugin.control_cli_plugin. properties_plugin.py:30   initialize_job  [id:16ebcb84-cc1a-4360-a234-f6731c3b0118-1705395355-83ff5]- Control Service REST API URL is not configured. Will not initialize Control Service based Properties client implementation.
{"name": "vdk.plugin.control_cli_plugin.execution_skip", "filename": "execution_skip.py", "lineno": 105, "funcName": "_skip_job_if_necessary", "message": "Checking if job should be skipped:", "level": "INFO", "timestamp": 1705395355.956534}
{"name": "vdk.plugin.control_cli_plugin.execution_skip", "filename": "execution_skip.py", "lineno": 106, "funcName": "_skip_job_if_necessary", "message": "Job : hello-world, Team : my-team, Log config: LOCAL, execution_id: 16ebcb84-cc1a-4360-a234-f6731c3b0118-1705395355", "level": "INFO", "timestamp": 1705395355.956574}
{"name": "root", "filename": "execution_skip.py", "lineno": 111, "funcName": "_skip_job_if_necessary", "message": "Local execution, skipping parallel execution check.", "level": "INFO", "timestamp": 1705395355.9566028}
{"name": "vdk.plugin.sqlite.sqlite_connection", "filename": "sqlite_connection.py", "lineno": 29, "funcName": "new_connection", "message": "Creating new connection against local file database located at: /var/folders/5d/bbd89v315777n_d24q2wznlh0000gr/T/vdk-sqlite.db", "level": "INFO", "timestamp": 1705395355.9570482}
{"name": "vdk.plugin.sqlite.sqlite_connection", "filename": "sqlite_connection.py", "lineno": 29, "funcName": "new_connection", "message": "Creating new connection against local file database located at: /var/folders/5d/bbd89v315777n_d24q2wznlh0000gr/T/vdk-sqlite.db", "level": "INFO", "timestamp": 1705395355.9573681}
{"name": "vdk.internal.builtin_plugins.connection.impl.wrapped_connection", "filename": "managed_cursor.py", "lineno": 170, "funcName": "_execute_operation", "message": "Executing query:\n-- job_name: hello-world\n-- op_id: 16ebcb84-cc1a-4360-a234-f6731c3b0118-1705395355\n-- SQL scripts are standard SQL scripts. They are executed against Platform OLAP database.\n-- Refer to platform documentation for more information.\n\n-- Common uses of SQL steps are:\n--    aggregating data from other tables to a new one\n--    creating a table or a view that is needed for the python steps\n\n-- Queries in .sql files can be parametrised.\n-- A valid query parameter looks like \u2192 {parameter}.\n-- Parameters will be automatically replaced if there is a corresponding value existing in the IJobInput properties.\n\nCREATE TABLE IF NOT EXISTS hello_world (id NVARCHAR);\n", "level": "INFO", "timestamp": 1705395355.957661}
{"name": "vdk.internal.builtin_plugins.connection.impl.wrapped_connection", "filename": "managed_cursor.py", "lineno": 97, "funcName": "execute", "message": "Executing query SUCCEEDED. Query duration 00h:00m:00s", "level": "INFO", "timestamp": 1705395355.957818}
{"name": "vdk.internal.builtin_plugins.connection.impl.wrapped_connection", "filename": "managed_connection_base.py", "lineno": 133, "funcName": "execute_query", "message": "Fetching query result...", "level": "INFO", "timestamp": 1705395355.9578428}
{"name": "vdk.internal.builtin_plugins.connection.impl.wrapped_connection", "filename": "managed_cursor.py", "lineno": 187, "funcName": "fetchall", "message": "Fetching all results from query ...", "level": "INFO", "timestamp": 1705395355.957864}
{"name": "vdk.internal.builtin_plugins.connection.impl.wrapped_connection", "filename": "managed_cursor.py", "lineno": 190, "funcName": "fetchall", "message": "Fetching all results from query SUCCEEDED.", "level": "INFO", "timestamp": 1705395355.9578822}
{"name": "vdk.internal.builtin_plugins.connection.impl.wrapped_connection", "filename": "managed_cursor.py", "lineno": 197, "funcName": "close", "message": "Closing DB cursor ...", "level": "INFO", "timestamp": 1705395355.9579039}
{"name": "vdk.internal.builtin_plugins.connection.impl.wrapped_connection", "filename": "managed_cursor.py", "lineno": 199, "funcName": "close", "message": "Closing DB cursor SUCCEEDED.", "level": "INFO", "timestamp": 1705395355.957922}
{"name": "vdk.internal.builtin_plugins.run.file_based_step", "filename": "file_based_step.py", "lineno": 105, "funcName": "run_python_step", "message": "Entering 20_python_step.py#run(...) ...", "level": "INFO", "timestamp": 1705395355.9585438}
{"name": "step_20_python_ste", "filename": "20_python_step.py", "lineno": 22, "funcName": "run", "message": "Starting job step step_20_python_ste", "level": "INFO", "timestamp": 1705395355.958584}
{"name": "vdk.internal.builtin_plugins.ingestion.ingester_router", "filename": "ingester_router.py", "lineno": 64, "funcName": "send_object_for_ingestion", "message": "Sending object for ingestion with method: sqlite and target: None", "level": "INFO", "timestamp": 1705395355.9586098}
{"name": "vdk.internal.builtin_plugins.run.file_based_step", "filename": "file_based_step.py", "lineno": 111, "funcName": "run_python_step", "message": "Exiting  20_python_step.py#run(...) SUCCESS", "level": "INFO", "timestamp": 1705395355.959177}
{"name": "vdk.plugin.sqlite.ingest_to_sqlite", "filename": "ingest_to_sqlite.py", "lineno": 76, "funcName": "ingest_payload", "message": "Ingesting payloads for target: /var/folders/5d/bbd89v315777n_d24q2wznlh0000gr/T/vdk-sqlite.db; collection_id: hello-world|16ebcb84-cc1a-4360-a234-f6731c3b0118-1705395355", "level": "INFO", "timestamp": 1705395357.965554}
{"name": "vdk.plugin.sqlite.sqlite_connection", "filename": "sqlite_connection.py", "lineno": 29, "funcName": "new_connection", "message": "Creating new connection against local file database located at: /var/folders/5d/bbd89v315777n_d24q2wznlh0000gr/T/vdk-sqlite.db", "level": "INFO", "timestamp": 1705395357.966198}
{"name": "vdk.internal.builtin_plugins.ingestion.ingester_base", "filename": "ingester_base.py", "lineno": 564, "funcName": "close_now", "message": "Ingester statistics: \n\t\tSuccessful uploads: 1\n\t\tFailed uploads: 0\n\t\tIngesting plugin errors: None\n\t\t", "level": "INFO", "timestamp": 1705395357.971732}
{"name": "vdk.internal.builtin_plugins.run.cli_run", "filename": "cli_run.py", "lineno": 169, "funcName": "create_and_run_data_job", "message": "Job execution result: SUCCESS", "level": "INFO", "timestamp": 1705395357.972028}
```

```ini
[vdk]
structlog_logging_format=ltsv
```

Output

```log
timestamp:1705395409.682153	level:INFO	logger_name:vdk.internal.cli_entry	file_name:cli_entry.py	line_number:135	function_name:vdk_main	message:Start CLI vdk with args ['run', '.']
timestamp:1705395409.698555	level:INFO	logger_name:vdk.internal.builtin_plugins.run.cli_run	file_name:cli_run.py	line_number:228	function_name:run	message:Versatile Data Kit (VDK)
Version: 0.3.1134532671
Build details: RELEASE_VERSION=0.3.1134532671, BUILD_DATE=Thu Jan 11 10:09:08 UTC 2024, BUILD_MACHINE_INFO=Linux runner-xumbkon8-project-28359933-concurrent-0krnrr 5.4.235-144.344.amzn2.x86_64 #1 SMP Sun Mar 12 12:50:22 UTC 2023 x86_64 GNU/Linux, GITLAB_CI_JOB_ID=5908208720, GIT_COMMIT_SHA=16c6a2fc25ed811f65637f5f215a173ad45d9d6c, GIT_BRANCH=main
Python version: 3.11.7 64bit (/opt/homebrew/opt/python@3.11/bin/python3.11)

Installed plugins:
vdk-sqlite (from package vdk-sqlite, version 0.1.954571638)
vdk-server (from package vdk-server, version 0.1.948436673)
vdk-structlog (from package vdk-structlog, version 0.1.1133681733)
vdk-logging-format (from package vdk-logging-format, version 0.1.1070203945)
vdk-control-service-properties (from package vdk-plugin-control-cli, version 0.1.948436673)
vdk-execution-skip (from package vdk-plugin-control-cli, version 0.1.948436673)
vdk-plugin-control-cli (from package vdk-plugin-control-cli, version 0.1.948436673)
vdk-ingest-file (from package vdk-ingest-file, version 0.1.948436673)
vdk-ingest-http (from package vdk-ingest-http, version 0.2.948436673)
--------------------------------------------------------------------------------
timestamp:1705395409.698694	level:INFO	logger_name:vdk.internal.builtin_plugins.run.cli_run	file_name:cli_run.py	line_number:150	function_name:create_and_run_data_job	message:Run job with directory /Users/mdilyan/Projects/vdk-playground/hello-world
2024-01-16 10:56:49,704 [VDK] hello-world [INFO ] vdk.plugin.control_cli_plugin. properties_plugin.py:30   initialize_job  [id:fc5c9c89-dce7-4de7-88bc-f1f4894f3ece-1705395409-cd855]- Control Service REST API URL is not configured. Will not initialize Control Service based Properties client implementation.
timestamp:1705395409.704321	level:INFO	logger_name:vdk.plugin.control_cli_plugin.execution_skip	file_name:execution_skip.py	line_number:105	function_name:_skip_job_if_necessary	message:Checking if job should be skipped:
timestamp:1705395409.7043478	level:INFO	logger_name:vdk.plugin.control_cli_plugin.execution_skip	file_name:execution_skip.py	line_number:106	function_name:_skip_job_if_necessary	message:Job : hello-world, Team : my-team, Log config: LOCAL, execution_id: fc5c9c89-dce7-4de7-88bc-f1f4894f3ece-1705395409
timestamp:1705395409.7043688	level:INFO	logger_name:root	file_name:execution_skip.py	line_number:111	function_name:_skip_job_if_necessary	message:Local execution, skipping parallel execution check.
timestamp:1705395409.7046232	level:INFO	logger_name:vdk.plugin.sqlite.sqlite_connection	file_name:sqlite_connection.py	line_number:29	function_name:new_connection	message:Creating new connection against local file database located at: /var/folders/5d/bbd89v315777n_d24q2wznlh0000gr/T/vdk-sqlite.db
timestamp:1705395409.704896	level:INFO	logger_name:vdk.plugin.sqlite.sqlite_connection	file_name:sqlite_connection.py	line_number:29	function_name:new_connection	message:Creating new connection against local file database located at: /var/folders/5d/bbd89v315777n_d24q2wznlh0000gr/T/vdk-sqlite.db
timestamp:1705395409.7051442	level:INFO	logger_name:vdk.internal.builtin_plugins.connection.impl.wrapped_connection	file_name:managed_cursor.py	line_number:170	function_name:_execute_operation	message:Executing query:
-- job_name: hello-world
-- op_id: fc5c9c89-dce7-4de7-88bc-f1f4894f3ece-1705395409
-- SQL scripts are standard SQL scripts. They are executed against Platform OLAP database.
-- Refer to platform documentation for more information.

-- Common uses of SQL steps are:
--    aggregating data from other tables to a new one
--    creating a table or a view that is needed for the python steps

-- Queries in .sql files can be parametrised.
-- A valid query parameter looks like → {parameter}.
-- Parameters will be automatically replaced if there is a corresponding value existing in the IJobInput properties.

CREATE TABLE IF NOT EXISTS hello_world (id NVARCHAR);

timestamp:1705395409.7053099	level:INFO	logger_name:vdk.internal.builtin_plugins.connection.impl.wrapped_connection	file_name:managed_cursor.py	line_number:97	function_name:execute	message:Executing query SUCCEEDED. Query duration 00h:00m:00s
timestamp:1705395409.7053282	level:INFO	logger_name:vdk.internal.builtin_plugins.connection.impl.wrapped_connection	file_name:managed_connection_base.py	line_number:133	function_name:execute_query	message:Fetching query result...
timestamp:1705395409.7053409	level:INFO	logger_name:vdk.internal.builtin_plugins.connection.impl.wrapped_connection	file_name:managed_cursor.py	line_number:187	function_name:fetchall	message:Fetching all results from query ...
timestamp:1705395409.705354	level:INFO	logger_name:vdk.internal.builtin_plugins.connection.impl.wrapped_connection	file_name:managed_cursor.py	line_number:190	function_name:fetchall	message:Fetching all results from query SUCCEEDED.
timestamp:1705395409.705371	level:INFO	logger_name:vdk.internal.builtin_plugins.connection.impl.wrapped_connection	file_name:managed_cursor.py	line_number:197	function_name:close	message:Closing DB cursor ...
timestamp:1705395409.7053828	level:INFO	logger_name:vdk.internal.builtin_plugins.connection.impl.wrapped_connection	file_name:managed_cursor.py	line_number:199	function_name:close	message:Closing DB cursor SUCCEEDED.
timestamp:1705395409.705893	level:INFO	logger_name:vdk.internal.builtin_plugins.run.file_based_step	file_name:file_based_step.py	line_number:105	function_name:run_python_step	message:Entering 20_python_step.py#run(...) ...
timestamp:1705395409.705926	level:INFO	logger_name:step_20_python_ste	file_name:20_python_step.py	line_number:22	function_name:run	message:Starting job step step_20_python_ste
timestamp:1705395409.705944	level:INFO	logger_name:vdk.internal.builtin_plugins.ingestion.ingester_router	file_name:ingester_router.py	line_number:64	function_name:send_object_for_ingestion	message:Sending object for ingestion with method: sqlite and target: None
timestamp:1705395409.7065542	level:INFO	logger_name:vdk.internal.builtin_plugins.run.file_based_step	file_name:file_based_step.py	line_number:111	function_name:run_python_step	message:Exiting  20_python_step.py#run(...) SUCCESS
timestamp:1705395411.713161	level:INFO	logger_name:vdk.plugin.sqlite.ingest_to_sqlite	file_name:ingest_to_sqlite.py	line_number:76	function_name:ingest_payload	message:Ingesting payloads for target: /var/folders/5d/bbd89v315777n_d24q2wznlh0000gr/T/vdk-sqlite.db; collection_id: hello-world|fc5c9c89-dce7-4de7-88bc-f1f4894f3ece-1705395409
timestamp:1705395411.713954	level:INFO	logger_name:vdk.plugin.sqlite.sqlite_connection	file_name:sqlite_connection.py	line_number:29	function_name:new_connection	message:Creating new connection against local file database located at: /var/folders/5d/bbd89v315777n_d24q2wznlh0000gr/T/vdk-sqlite.db
timestamp:1705395411.720793	level:INFO	logger_name:vdk.internal.builtin_plugins.ingestion.ingester_base	file_name:ingester_base.py	line_number:564	function_name:close_now	message:Ingester statistics:
		Successful uploads: 1
		Failed uploads: 0
		Ingesting plugin errors: None

timestamp:1705395411.721028	level:INFO	logger_name:vdk.internal.builtin_plugins.run.cli_run	file_name:cli_run.py	line_number:169	function_name:create_and_run_data_job	message:Job execution result: SUCCESS
```

User configuration takes precedence over global configuration

**Bound Loggers**

Users are able to pass additional metadata fields when logging. This comes out
of the box with the python logging module.

Example:

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

Now every time you call the bound logger, you have the uuid attached.

```log
2024-01-16 10:31:04,761 [VDK] [INFO ] step_20_python_ste                20_python_step.py :22   run               - Starting job step step_20_python_ste
2024-01-16 10:31:04,761 [VDK] [INFO ] step_20_python_ste                20_python_step.py :25   run              ed1e447d-3746-4068-8a83-353176327985 - This is an info log statement with extra stuff
2024-01-16 10:31:04,761 [VDK] [INFO ] step_20_python_ste                20_python_step.py :26   run              ed1e447d-3746-4068-8a83-353176327985 - This is another log statement with uuid
```

Bound loggers act the same as regular loggers. You can even pass extra params to them, or bind additional context.

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

**Syslog Support**

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

### Log Less

Every call to `log.info()`, `log.debug()`, `log.exception()` is audited. Logs
are moved to the appropriate level if necessary. Redundant logging is removed.

Users have the ability to change the log level for specific modules in their
data job with the `log_level_module` option.

```ini
[vdk]
log_level_module="vdk.plugin.sqlite=INFO;vdk.internal.core=ERROR"
```

### Clean Error Handling

**Remove the log-and-(re)throw pattern**

VDK has an error reporting and classification mechanism. If an error occurs, it
decides who should fix the error, e.g. the user or the platfrom team. The
mechanism works by analyzing the exception stack trace and any attribute fields
that are attached to the exception.

Previously, this mechanism was tied to logging. To throw an exception from vdk
code, you had to call the `log_and_throw()` or a `log_and_rethrow()` function,
depending on if you're throwing a new exception or want to pass an existing one
up the call stack. This had the unfortunate side effect that every time you
passed an error up the call stack, you also logged it. VDK errors were wrapped
in other VDK errors when getting logged in certain cases.

This problem is now fixed by separating error reporting from logging. Only
reporting is tied to throwing/rethrowing exceptions, which lets us log them
however we see fit.

Note: Work is ongoing and reporting exceptions and throwing them will no longer
happen in the same function after
https://github.com/vmware/versatile-data-kit/issues/3022

**Single point of exception logging**

Errors coming from VDK or from libraries used in data jobs all filter down to
the same exception handler for logging. There are other exception handlers in
VDK, but the one that outputs the final stack trace is at the end of the data
job cycle. The stack trace is not logged anywhere else. This makes the log
shorter and more readable. It also lets us decide if we'd like to pass the
exception to the user or not.

https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/internal/builtin_plugins/run/data_job.py#L297

**Don't wrap exceptions**

Because of the above two changes, we're able to stop wrapping non-vdk exceptions
in custom vdk errors. Instead, we just pass them up the stack and to the user
for handling. Users don't need to be familiar with VDK-specific exceptions to
handle errors in their data jobs.

```python
import logging

import pandas as pd
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    args = dict()
    try:
        # Something questionable
        # like reading an empty CSV inside the template
        job_input.execute_template("csv-risky", args)
    except pd.errors.EmptyDataError as e: # handle the pandas exception directly
        log.info("Handling empty data error")
        log.exception(e)
```

**Introduce specific exception classes**

We've moved away from throwing generic errors, like `UserCodeError`, `PlatformError` or `VDKConfigurationError` to using more specific error classes that inherit from `BaseVdkError`

https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/internal/core/errors.py#L103

The resolvable_by and resolvable_by_actual attributes are processed by the error
reporting mechanism.

https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/internal/builtin_plugins/ingestion/exception.py#L10


**Exception formatting**

VDK had a strict exception logging template, similar to

```
WHAT_HAPPENED:
WHY_DID_IT_HAPPEN:
WHOM_TO_BLAME:
COUNTERMEASURES:
```

This lead to bad practices like putting generic text in the template.

```
WHAT_HAPPENED: Exception occured
WHY_DID_IT_HAPPEN: Consult stack trace
WHOM_TO_BLAME: USER
COUNTERMEASURES: Fix exception
```

We've removed this format in favor of free-form text. This removes the incentive
to write generic text, since callers don't feel like they have to fill out a
form every time.

We've also added exception pretty printing that can be enabled/disabled using a
config option. This is only valid for VDK exceptions.

```ini
[vdk]
log_exception_formatter=pretty
```

```log
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+   VdkConfigurationError: An error of type Configuration error occurred. Error should be fixed by Platform   +
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+  Provided configuration variable for DB_DEFAULT_TYPE has invalid value.                                     +
+  VDK was run with DB_DEFAULT_TYPE=sqlite, however sqlite is invalid value for this variable.                +
+  I'm rethrowing this exception to my caller to process. Most likely this will result in failure of           +
+  current Data Job.                                                                                          +
+  Provide either valid value for DB_DEFAULT_TYPE or install database plugin that supports this type.         +
+  Currently possible values are []                                                                           +
+                                                                                                             +
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

```

```ini
[vdk]
log_exception_formatter=plain
```

```log
vdk.internal.core.errors.VdkConfigurationError: VdkConfigurationError: An error of resolvable type ResolvableByActual.PLATFORM occurred
Provided configuration variable for DB_DEFAULT_TYPE has invalid value. VDK was run with DB_DEFAULT_TYPE=sqlite, however sqlite is invalid value for this variable.
I'm rethrowing this exception to my caller to process.Most likely this will result in failure of current Data Job. Provide either valid value for DB_DEFAULT_TYPE or
install database plugin that supports this type. Currently possible values are []

```

**Put extra logging info behind config options**

### Progress Indicators

Data jobs in the CLI display progress indicators by default instead of logs to
stdout/stderr. Users are given the option to switch between the progress
indicator and logging using an option in config.ini. This switch is available at
the global level when deploying vdk to production environments.

On error, the error message gives the root cause and line number of the failure.
The full logs are available inside a temp file. The link to the temp file is
also part of the CLI error message.

Updating progress indicators is asynchronous, ensuring primary task doesn’t get
interrupted or slowed down due to progress bar updates. This is really relevant
for ingestion.

Users ingest data by calling job_input.send_object_for_ingestion and
job_input.send_tabular_data_for_ingestion The calls are asynchronous, e.g.
send_xxx adds the payload to queue and returns immediately. Users can call
send_tabular_data_for_ingestion which adds to the number of payloads that are
tracked.

Also as we need progress indicators in multiple places likely we need a common
encapsulation (or abstraction) for that - in a form of a python module or plugin.

There is a common abstraction for spawning progress indicators in multiple
places. Progress indicators provide a notification callback mechanism so it's
integratable with Notebooks

[User workflow research](https://github.com/vmware/versatile-data-kit/wiki/Research:-Progress-Indicators)

#### Technical Requirements

* The progress abstraction supports multi step operations. Different steps are
  started and ended multiple times one after another in a job.
* The abstraction supports hierarchical operations. A Step can start other long
  running operations (e.g a DAG sub-jobs)
* The abstraction supports operations running concurrently (that is multiple
  tasks are started and keep progressing concurrently - in the same thread).
  This requirement comes primarily because of DAGs. Multiple sub-jobs started in
  a DAG can run concurrently (no multi-threading needed here, though)
* The abstraction should support operations running in background threads. When
  you send data for ingestion, that data is processed in background while the
  job continue with other operations. The progress track can be updated from
  multiple threads as they ingest data
* The abstraction should allow for the total to change. E.g when we are
  ingesting data the total number of objects being ingested is changed as user
  adds new and new ones.
* Performance overhead should be minimal as this may be called millions of times
  (e.g for each ingested row in a payload)
* (Optional) The abstraction can be extended to collect metrics  about the state
  of operations running by the framework (bandwidth, duration, failed requests,
  etc). This is currently used by vdk-core ingestion logic.


##### Core Components

![progress tracker presenter](progress-tracker-presenter.svg)

###### ProgressTracker

This is a core component designed for monitoring the progress of operations. It
is integrated into vdk-core and will provide essential tracking features based
on above technical requirements. The Progress Tracker supports a tree-like
hierarchical structure, allowing for the initiation of multiple sub-tasks under
a high-level task.

Here's a breakdown illustrating how the Progress Tracker might operate during the execution of a data job with two steps:

![progress-tracker-break-down.svg](progress-tracker-break-down.svg)


###### API Methods

- create_sub_tracker(): To create a new sub-tracker for nested tasks.
- add_iterations(n): To add n number of new iterations (items) for tracking.
- update_progress(n): To update the progress by n iterations.


The interface expose to the user and to plugins would look like this
```python
class IProgressTracker:
    """
    A class for tracking the progress of a task and its sub-tasks.
    """

    def add_iterations(self, new_iterations: int):
        """
        Adds new iterations to the total count for this tracker.

        :param new_iterations: The number of new iterations to add.
        """


    def update_progress(self, iterations: int = 1):
        """
        Update progress with how many iteration have we completed.
        Generally only childless trackers should be directly updated.
        Parent trackers are automatically updated by their children.
        """

    def create_sub_tracker(self, title: str, total_iterations: int) -> ProgressTracker:
        """
        Create a new child tracker. The child tracker will point to its parent.
        So any iterations added to the child tracker are automatically tracked by the parent as well.
        And will update the parent automatically with any progress.
        Any tracked metric is propagated to the parent as well
        """

    def track_metric(self, key: str, value: float):
        """
        The tracked metric must be cumulative since it's aggregated in the parent.
        Non-cumulative metrics (like rate, latency, mean, median) will not provide result.
        Example of cumulative metrics are  records processed, errors, time spent, number of requests, successful requests, failed requests.
        """
        self._metrics[key] = self._metrics.get(key, 0) + value
        if self._parent:
            self._parent.track_metric(key, value)

    def get_metrics(self) -> Dict[str, int]:
        """
        Return dictionary with currently collected metrics about what is being tracked.
        """
```

###### ProgressPresenter

The ProgressPresenter is an interface in vdk-core that serves as the blueprint
for different strategies to present or display the progress of operations in
various environments. In essence, ProgressPresenter abstracts the "presentation
layer" of progress tracking, making it versatile enough to fit different
contexts—whether that's basic logging to the standard output, graphical bars in
a terminal, or interactive displays in a notebook environment.

A logging presenter is implemented in vdk-core (used by default) while other
strategies like CLI and notebook are implemented in separate plugins like
vdk-tqdm and vdk-jupyter.

###### Workflow
![progress-tracker-sequence.svg](progress-tracker-sequence.svg)

- On CLI execution start (and data job start) we create a progress tracker and
  store it in
  [CoreContext](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/internal/core/context.py).
    - Then when a new data job step starts we create a child tracker to track
      the step.
        - (Optional) When an SQL query starts we create a child tracker for the
          SQL query.
        - When A DAG job is started within a step a new subtracker is created
          (tracking all dag jobs). When the job completes the tracker is
          updated.
    - When
      [Ingestor](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/internal/builtin_plugins/ingestion/ingester_base.py)
      is initialized we can start a child tracker to track ingestion
        - Each time new data is added to a queue, we use tracker.add (#
          payloads, likely in _send method)
            - A new hook is added every time a new payload is send (ingest_send_payload hook)
        - Each time data is sent, we update progress. (we can use an existing hook : [post_ingest_process](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/plugin/plugin_input.py#L486) )

The ProgressTracker would be exposed and available in JobInput interface so it
can be used by DAGs .

For DAG it can be used  in this way
```python
current_step_progress_tracker = job_input.get_progress_tracker()

dag_tracker = current_step_progress_tracker.create_sub_tracker()
```

###### vdk-tqdm plugin

For implementing CLI-based progress tracking TQDM (via vdk-tqdm plugin)
It provides capabilities for both Notebook (through tqdm.notebook package) and terminal (tqdm.tqdm package)

In tqdm, implementing nested progress bars involves using the position and leave parameters.
The position parameter sets which row the progress bar will appear in the console,
while leave controls whether the progress bar stays visible after completion.

Since trackers are never removed we can simply count all currently created trackers to set a position.

##### Pseudo code

Check out sample [implementation](./progress_tracker_pseudo_code.py) of core ProgressTracker to better understand the desgin in practice

## Implementation stories

### [Log Structure](https://github.com/vmware/versatile-data-kit/milestone/14) - In Progress

### [Log Less](https://github.com/vmware/versatile-data-kit/milestone/15) - Completed

### [Clean Error Handling](https://github.com/vmware/versatile-data-kit/milestone/16) - Completed

### [Progress Indicators](https://github.com/vmware/versatile-data-kit/milestone/17) - De-scoped


#### Implement ProgressTracker in vdk-core
Description: As a user, I want the tracking system to automatically initialize when I start a CLI execution so that I don't have to manually set it up.
Acceptance Criteria: Progress tracking starts automatically with CLI execution.
#### Create Child Tracker for New Steps
Description: As a user, I want to see the progress for each specific step in my task so that I can understand how much work remains.
Acceptance Criteria: Separate progress tracking for each step.
#### Add SQL Query Support
Description: As a user, I want the option to track the progress of SQL queries so that I can monitor them separately if needed.
Acceptance Criteria: Progress tracking for SQL queries.
#### Track DAG Job Progress
Description: As a user, I want to monitor the progress of each sub-job in a DAG so that I can understand the status of my complex tasks.
Acceptance Criteria: Sub-task tracking for each DAG job.
#### Ingestion Tracker
Description: As a user, I want to know the progress of data ingestion so I can be aware of how much data has been processed.
Acceptance Criteria: Tracking of data ingestion progress
#### Implement Basic Logging Strategy
Description: As a user, I want to see progerss info logged in logs on some interval  so that I can debug or monitor basic activities easily. This would be used in Cloud deployment
Acceptance Criteria: Basic logging is visible and clear.
#### CLI Progress with TQDM Plugin
Description: As a user, I want a specialized, visually pleasing CLI interface for tracking progress using the TQDM library, so that my CLI experience is enhanced.
Acceptance Criteria: Progress tracking in the CLI utilizes the TQDM library through a separate vdk-tqdm plugin and offers an interactive interface.
#### TQDM Support in Notebooks
Description: As a user working in Jupyter Notebooks, I want the tracking system to also leverage the TQDM library, so that I can have a consistent, visually pleasing progress bar in notebooks.
Acceptance Criteria: TQDM is utilized for tracking progress in Jupyter Notebooks, integrated through the vdk-tqdm plugin
#### Configurable Tracking Strategy and configureable tracker
Description: As a user, I want to be able to configure which strategy to use for progress tracking (notebook, terminal, log, etc.) and specify what components I want to track (job, steps, queries, etc.), so that I can tailor the tracking to my specific needs.
Acceptance Criteria: Configuration options for specifying tracking strategy and components are available and operational.


### [Documentation](https://github.com/vmware/versatile-data-kit/milestone/18)

### [Promotional Materials](https://github.com/vmware/versatile-data-kit/milestone/19)


## Alternatives
<!--
Optionally, describe what alternatives has been considered.
Keep it short - if needed link to more detailed research document.
-->
### Progress trackers 3th party libraries research

For python there are multiple progress bars (e.g https://datagy.io/python-progress-bars/)

TQDM is chosen for its support for jupyter notebooks, lower performance overhead and high popularity.

| Feature                        | TQDM     | Alive-Progress | Progressbar2 | Notes                                                                                                                                   |
| :----------------------------- | :------- | :------------- | :----------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| Ease of Use                    | High     | High           | Moderate     | TQDM and Alive-Progress have intuitive APIs. Progressbar2 requires more boilerplate code.                                               |
| Customization                  | Moderate | High           | High         | Alive-Progress and Progressbar2 offer more customization options for visualization.                                                     |
| Built-in Themes/Styles         | Yes      | Yes            | No           | TQDM has fewer styles.                                                                                                                  |
| Performance Overhead           | Low      | Moderate       | Moderate     | TQDM is designed for minimal overhead, which is beneficial for tasks that require frequent updates.                                     |
| Real-time Updates              | Yes      | Yes            | Yes          | All provide real-time updates                                                                                                           |
| Concurrency Support            | Limited  | No             | Limited      | None of the libraries excel in multi-threading or async support. TQDM and Progressbar2 offer some limited capabilities (async support). |
| Interactive Mode (Notebook)    | Yes      | No             | No           | TQDM stands out for its Jupyter Notebook integration.                                                                                   |
| Nested Progress Bars           | Yes      | Yes            | No           | TQDM and Alive-Progress support hierarchical progress tracking.                                                                         |
| Dynamic Total Updates          | Yes      | Yes            | Yes          | All allow for changing the total count dynamically.                                                                                     |
| Time Estimations               | Yes      | Yes            | Yes          | All offer time estimation for completion.                                                                                               |
| Progress Bar Custom Text       | Yes      | Yes            | Yes          | All support custom text.                                                                                                                |
| Logging Compatibility          | Yes      | Limited        | Yes          | TQDM and Progressbar2 can easily integrate with standard Python logging.                                                                |
| Community Support / Popularity | High     | Moderate       | Moderate     | TQDM is the most widely used and has a large community for support.                                                                     |
