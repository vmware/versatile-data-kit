
# VEP-2448: VDK Run Logs: Simplified And Readable

* **Author(s):** Dilyan Marinov (mdilyan@vmware.com), Antoni Ivanov (aivanov@vmware.com)
<!-- * **Status:** draft | implementable | implemented | rejected | withdrawn | replaced -->
* **Status:** draft


To get started with this template:

- [x] **Create an issue in Github (if one does not exists already)**
- [x] **Make a copy of this template directory.**
  Copy this template into the specs directory and name it
  `NNNN-short-descriptive-title`, where `NNNN` is the issue number (with no
  leading-zero padding) created above.
- [ ] **Fill out this file as best you can.**
  There are instructions as HTML comments.
  At minimum, you should fill in the "Summary" and "Motivation" sections.
- [ ] **Create a PR for this VEP.**
- [ ] **Merge early and iterate.**
  Avoid getting hung up on specific details and instead aim to get the goals of
  the VEP clarified and merged quickly. The best way to do this is to just
  start with the high-level sections and fill out details incrementally in
  subsequent PRs.

<!-- Provide table of content as it's helpful. -->

- [VEP-2448: VDK Run Logs: Simplified And Readable](#vep-2448-vdk-run-logs-simplified-and-readable)
  - [Summary](#summary)
  - [Glossary](#glossary)
  - [Motivation](#motivation)
    - [Logs on failures](#logs-on-failures)
    - [Logs on success](#logs-on-success)
    - [Debug mode](#debug-mode)
    - [Progress Tracking](#progress-tracking)
    - [VDK exception handling and  categorization](#vdk-exception-handling-and--categorization)
  - [Requirements and goals](#requirements-and-goals)
  - [High-level design](#high-level-design)
    - [Log Structure](#log-structure)
    - [Log Less](#log-less)
      - [Logs not at the apprpopriate level](#logs-not-at-the-apprpopriate-level)
      - [Multi-layered logging](#multi-layered-logging)
    - [Don't Repeat Yourself (DRY)](#dont-repeat-yourself-dry)
    - [Clean Error Handling](#clean-error-handling)
    - [Progress Indicators](#progress-indicators)
  - [API design](#api-design)
  - [Detailed design](#detailed-design)
  - [Implementation stories](#implementation-stories)
  - [Alternatives](#alternatives)

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

At the moment, VKD users face multiple challenges related to logging in data job
runs. Based on user feedback we've received, these can be split into 5 categories.

### Logs on failures

Useful information gets lost in the noise or sometimes just
missing This is especially true for user errors. There are also some error
messages that just don't contain any useful information to begin with We might
have incentivized some bad practices with our error message format. Some people
tend to just write placeholder text, e.g. "WHAT HAPPENED: An error occurred", or
"COUNTERMEASURES: Check exception". These kinds of messages are extremely
annoying from an user perspective. When a step fails, we don't point to the
actual line of the code where the failure happened Actual root causes are
sometimes buried in the stack There's lots of meta-logs, impala query logs, etc.
This leads us to believe that we have a lot of info logging that should actually
be on the debug level.

### Logs on success

Users expect little or no log output on success. Users tend to add their own
logging to signify when a step started or ended they expect these kinds of logs
to be highlighted somehow, or be the only logs they see

### Debug mode

Some users have trouble running jobs in debug mode and getting debug level logs
This points to a gap in our documentation

### Progress Tracking

Users want better tracking of job progress (for DAGs, steps, ingestion)

### VDK exception handling and  categorization

There is a need for more clarity and categorization in error messages, likely
more structured error reporting, such as knowing whether an error is a syntax
error, data error, library issue, or platform error, as very important
visibility of the steps or components where failures occur so people can quickly
find out the principal issue

Logging and error handling should be improved in ways that adress all these
challenges. This will result in less time spent troubleshooting, fewer support
queries, more data job runs that are successful and an overall better user
experience.

## Requirements and goals
<!--
It tells **what** is it trying to achieve?
List the specific goals (functional and nonfunctional requirements)? How will we
know that this has succeeded?

Specify non-goals. Clearly, the list of non-goals can't be exhaustive.
Non-goals are only features, which a contributor can reasonably assume were a goal.
One example is features that were cut during scoping.
-->
1. Data job run logs provide useful and readable information
   1. Data job run logs provide progress tracking information
      1. current step
      1. ingested data
      1. the amount of resources currently consumed
      1. progress bars for local runs
   1. User logs stand out
   1. DAGs are traceable in the logs
      1. Logs show current job name
      1. Logs show parent job name for the current job
      1. DAG jobs that run in parallel can be sorted and grouped, so that logs for a single job are extracted
   1. Debug information is at the appropriate level, e.g. impala query meta logs are at debug level and not info
1. Finding information for failed runs is straightforward
   1. The root cause is immediately visible from the logs.
   1. When an error occurs, relevant information is visible on top of the error log. This includes
      1. why it happened
      1. where it happened (data job stage and line)
      1. most common troubleshooting steps
1. Changing the logging level is straightforward
   1. Changing the logging level is documented
   1. Changing the logging level is available in the cloud
1. The above points are valid for local and cloud data job runs.

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

Based on user feedback, we've identified 5 workstreams.

### Log Structure

```
2023-07-27 17:50:44,918 [VDK] hackernews-top-stories [INFO ] vdk.plugin.control_cli_plugin. properties_plugin.py:30   initialize_job  [id:30618c1b-677b-4f96-86a3-dda26011b3d8-1690469444-20a99]- Control Service REST API URL is not configured. Will not initialize Control Service based Properties client implementation.
```

`[Local][Cloud]` The current logging format is static and looks something like `<timestamp> [VDK] <job-name> <level> <plugin:line> <step> <id> <message>`. We need a way to configure
this format dynamically on the data job and on the environment level.

A few ideas on how to do it:

- expose the logging format as an env variable that's overridable per job
- provide a configuration step that lets users call an api and configure the
  format, e.g.
```
logs.format().use()
  .timestamp()
  .job_name()
  .level()
```
  - not sure how it will work on an environment level, maybe we can provide it
    on the CLI / in the helm config
- it should be extendable, e.g. if we want to add some new classification to the
  format (parent job, team name), it should be easy to do in a modular fasion

### Log Less

#### Logs not at the apprpopriate level

`[Local][Cloud]` We have to go through every log statement in every VDK plugin and make sure it's
at the appropriate level. Judging by user feedback, we have a lot of INFO
logging that should be at the DEBUG level.

`[Local][Cloud]` There should be an easy way to for the user configure the datajob log level
dynamically.

Note: There is currently log_level_module which you can set to
a.b.c=INFO;foo.bar=ERROR. We have to decide if this level of granularity is
sufficient. We should also improve the documentation around it.

#### Multi-layered logging

`[Local]` Logs on failure should point to the problem and provide the minimum
amount of troubleshooting information to get started. Error messages in the
console should show the root cause and the line where the error happened. Any
other information, e.g. full stack trace, should be output to a temp file.

```
process_twitter_data Step 10_ingest_data.py Line: 38
File with path "./some_file.txt does not exist
Full error log /tmp/30618c1b-677b-4f96-86a3-dda26011b3d8-1690469444-20a99/error.log
```
`[Cloud]` Full error log should be output to stderr

### Don't Repeat Yourself (DRY)

`[Local][Cloud]` Remove any repeating info in success logs. Success logs should
show which step has started or ended and the success status at the end. Note
that locally, this could be entirely replaced by progress bars, but users should
be able to choose between one or the other.

### Clean Error Handling

`[Local][Cloud]` Do away with the log-and-throw and log-and-rethrow patterns.
Errors should be passed up the call stack to the original caller. Errors should
be caught and wrapped or replaced by other errors only if we're adding more
information to the existing error.

To preserve information, we can use an error context, parse it and dump it to
stdout or a log file, depending on configuration. Recoverable errors should not
be passed up the call stack, but just logged at the `WARN` level. Errors we
can't recover from should be added to the context and re-thrown.

`[Local][Cloud]` Error classification is good, because it eliminates firction
between users and support teams.

The current error handling mechanism has encouraged some bad practices, such as
making the caller add irrelevant information, e.g.

```
"WHAT HAPPENED: An error occurred",
"COUNTERMEASURES: Check exception"
```

We don't provide sufficient granularity in the errors that can be thrown and
rely on the caller to "do the right thing", in this case, add relevant
information. Error classification should be modified to use a class hierarchy of
generic errors. These errors should help classify the problem, e.g. we should
have UserError, PlatformError and errors that inherit from them instead of
making the caller log all the error information.

### Progress Indicators

`[Local]` Replace logs with progress indicators entirely. Give the user the
option to choose between progress indicators and logs for local jobs.

We should think about exporting progress tracking as a unified module, because
we can track progress on multiple levels. There are three levels of tracking
- DAGs
- Jobs
- Job Steps

Additonally, we could consider a fourth level - users tracking progress inside
data jobs steps, e.g. percentage of data ingested. This would require exposing
an API for the users.

`[Cloud]` If we build a progress tracking module, we should have a good way to
leverage it for cloud deployments. Cloud jobs will not use progress bars, but
could still make use of this system and display logs instead.

Resources:

- https://pypi.org/project/progress2/
- https://tqdm.github.io/
- https://joblib.readthedocs.io/en/stable/

## API design

<!--

Describe the changes and additions to the public API (if there are any).

For all API changes:

Include Swagger URL for HTTP APIs, no matter if the API is RESTful or RPC-like.
PyDoc/Javadoc (or similar) for Python/Java changes.
Explain how does the system handle API violations.
-->


## Detailed design
<!--
Dig deeper into each component. The section can be as long or as short as necessary.
Consider at least the below topics but you do not need to cover those that are not applicable.

### Capacity Estimation and Constraints
    * Cost of data path: CPU cost per-IO, memory footprint, network footprint.
    * Cost of control plane including cost of APIs, expected timeliness from layers above.
### Availability.
    * For example - is it tolerant to failures, What happens when the service stops working
### Performance.
    * Consider performance of data operations for different types of workloads.
       Consider performance of control operations
    * Consider performance under steady state as well under various pathological scenarios,
       e.g., different failure cases, partitioning, recovery.
    * Performance scalability along different dimensions,
       e.g. #objects, network properties (latency, bandwidth), number of data jobs, processed/ingested data, etc.
### Database data model changes
### Telemetry and monitoring changes (new metrics).
### Configuration changes.
### Upgrade / Downgrade Strategy (especially if it might be breaking change).
  * Data migration plan (it needs to be automated or avoided - we should not require user manual actions.)
### Troubleshooting
  * What are possible failure modes.
    * Detection: How can it be detected via metrics?
    * Mitigations: What can be done to stop the bleeding, especially for already
      running user workloads?
    * Diagnostics: What are the useful log messages and their required logging
      levels that could help debug the issue?
    * Testing: Are there any tests for failure mode? If not, describe why._
### Operability
  * What are the SLIs (Service Level Indicators) an operator can use to determine the health of the system.
  * What are the expected SLOs (Service Level Objectives).
### Test Plan
  * Unit tests are expected. But are end to end test necessary. Do we need to extend vdk-heartbeat ?
  * Are there changes in CICD necessary
### Dependencies
  * On what services the feature depends on ? Are there new (external) dependencies added?
### Security and Permissions
  How is access control handled?
  * Is encryption in transport supported and how is it implemented?
  * What data is sensitive within these components? How is this data secured?
      * In-transit?
      * At rest?
      * Is it logged?
  * What secrets are needed by the components? How are these secrets secured and attained?
-->


## Implementation stories
<!--
Optionally, describe what are the implementation stories (eventually we'd create github issues out of them).
-->

## Alternatives
<!--
Optionally, describe what alternatives has been considered.
Keep it short - if needed link to more detailed research document.
-->
