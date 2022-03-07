# VEP-554: Apache Airflow Integration

* **Author(s):** Miroslav Ivanov (miroslavi@vmware.com), Antoni Ivanov (
  aivanov@vmware.com)
* **Status:** draft

To get started with this template:

- [ ] **Create an issue in Github (if one does not exists already)**
- [ ] **Make a copy of this template directory.**
  Copy this template into the specs directory and name it
  `NNNN-short-descriptive-title`, where `NNNN` is the issue number (with no leading-zero
  padding) created above.
- [ ] **Fill out this file as best you can.**
  There are instructions as HTML comments. At minimum, you should fill in the "Summary"
  and "Motivation" sections.
- [ ] **Create a PR for this VEP.**
- [ ] **Merge early and iterate.**
  Avoid getting hung up on specific details and instead aim to get the goals of the VEP
  clarified and merged quickly. The best way to do this is to just start with the
  high-level sections and fill out details incrementally in subsequent PRs.

- [Summary](#summary)
- [Glossary](#glossary)
- [Motivation](#motivation)
- [Requirements and Goals](#requirements-and-goals)
    - [Goals](#goals)
    - [Non-goals](#non-goals)
- [High-level design](#high-level-design)
- [System Interface (API)](#api-design)
- [Detailed design](#detailed-design)
    - [VDK Provider](#vdk-provider)
        - [VDK Hook](#vdk-hook)
        - [VDK Operator](#vdk-operator)
        - [VDK Sensor Operator](#vdk-sensor-operator)
        - [Connection](#connection)
        - [Sample DAG](#sample-dag)
- [Security and Permissions](#security-and-permissions)
- [Implementation Stories](#implementation-stories)
- [Alternatives](#alternatives)

## Summary

This VEP outlines the architectural changes required to provide VDK users with the
ability to do multi-jobs non-linear analytics. The support for definition of dependencies
between Data Jobs will be introduced by integrating VDK with Apache Airflow.

The integration itself will be achieved through the VDK Provider implementation. The
provider will be deployed on private Airflow deployment and will be responsible for
managing Data Jobs.

## Glossary

* **VDK**: https://github.com/vmware/versatile-data-kit/wiki/dictionary#vdk
* **Control
  Service**: https://github.com/vmware/versatile-data-kit/wiki/dictionary#control-service
* **Data Job**: https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job
* **Data Job
  Step**: https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job-step
* **Data Job
  Execution**: https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job-execution
* **Apache Airflow (Airflow)**: https://airflow.apache.org/
* **VDK Provider**: VDK Airflow Community
  Provider (https://airflow.apache.org/docs/apache-airflow-providers/)
* **DAG**: Directed Acyclic Graph
* **Data Mart**: Database with a set of tables

## Motivation

Тhe need for multi-job non-linear analytics is growing. Users need to be able to define
dependencies between Data Jobs. For instance, they need to ingest from multiple systems
into Data Lake to model the data. All lake tables are used afterwards by subsequent
processing jobs to generate Data Marts. The processing jobs start only after the
ingestion jobs are over.

Currently, VDK supports only multi-step linear analytics by defining sequential steps
within a single process (job). The steps can be written either in SQL or Python. Due to
the fact that the steps are linear and with limited ability to run in parallel, more
complex non-linear analytics cannot be done.

There are two workarounds to solve this:

1. Ingestion and processing jobs can be defined as sequential steps in a single job.
   However, this approach has several drawbacks:
    * The steps are sequential with limited ability to run in parallel.
    * The execution time of the Data Job is limited (currently up to 12 hours).

2. Ingestion and processing jobs can be scheduled at a certain time with an appropriate
   time offset between them (e.g. the ingestion jobs start at 2 p.m., as the processing
   jobs starts 8 p.m.). However, this approach is not reliable as the users need to know
   how long the jobs will take, some jobs may take more time than usual.

The support for the definition of dependencies between the jobs will be introduced, in
order to provide the ability to do multi-job non-linear analytics to our users. It will
be achieved through the integration of VDK with Apache Airflow.

Airflow has been chosen because it is a tool that can create, organize, and monitor
workflows. It is open-source, hence it is free and has a wide range of support as well.
It is one of the most trusted platforms that is used for orchestrating workflows and is
widely used and recommended by top data engineers. This tool provides many features like
a proper visualization of data pipelines and workflows, workflow status, data logs, and
codes in detail. Airflow is a distributed system that is highly scalable and can be
connected to various sources, which makes it flexible. These features allow it to be used
efficiently in the orchestration of complex workflow and data pipelining problems.

## Requirements and Goals

### Goals

#### Provide an ability to define dependencies between Data Jobs

A user wants to start a second job after the first job is over. For example, the user has
several jobs, after each job is complete, the user would like to start a common
post-processing job.

Use cases:

* Sync between multiple synchronous ingestion and processing jobs - the user needs to be
  able to ingest from multiple systems into Data Lake to model the data. All lake tables
  are used afterwards by subsequent processing jobs to generate Data Marts. The
  processing jobs start only after the ingestion jobs are over.
* Ability to restart the failed workflow - when a single workflow task fails, the user
  should be able to restart the workflow, and only failed jobs and those associated with
  them should be executed.
* Trigger a job based on previous job status in the DAG - when there is "Data Mart tables
  dependencies (DAG)", some jobs should be available as optional (e.g. DAG should not
  fail if steps fail).

#### Contribute a custom provider to Airflow Community

#### Executing Data Jobs should be enabled by private Airflow deployments

User cases:

* Users want to create operational and analytics pipelines of jobs.
* Users already own their Airflow deployment.

#### Comparison of VDK with Apache Airflow

### Non-goals

#### VDK will not be installing or managing Apache Airflow through the Helm Chart

## High-level design

![high-level-diagram.png](high-level-diagram.png)

Apache Airflow 2 is built in a modular way. The "Core" of Apache Airflow provides core
scheduler functionality which allows you to write some basic tasks, but the capabilities
of Apache Airflow can be extended by installing additional packages, called providers.

Providers can contain operators, sensors, hooks, and transfer operators to communicate
with a multitude of external systems, but they can also extend Airflow core with new
capabilities.

The proposed design describes the solution for supporting multi-jobs non-linear analytics
by integrating VDK with Apache Airflow. For this purpose, an Apache Airflow Provider
called "VDK Provider" will be implemented and responsible for managing Data Jobs. It will
give us the ability to define DAGs in which the tasks (jobs) will be defined by
instantiating custom operators. The operators will start and monitor Data Job executions
via the Control Service Execution API.

In order to speed up the VDK popularization and provide easier integration with Airflow
to our users, the VDK Provider will be contributed to the Airflow Community.

## API design

No changes to the public API.

## Detailed design

### VDK Provider

The integration of VDK with Apache Airflow will be accomplished by VDK Provider
implementation. It will provide an ability to the users to define Airflow Workflow that
consists of Data Jobs. Basically, it will be responsible for managing Data Job
executions (starting, canceling, retrieving). As can be seen from the below diagram the
provider will consist of a hook, operator, and sensor.

![class-diagram.png](class-diagram.png)

Users will be able to choose from two operating modes - synchronous and asynchronous,
depending on their Data Jobs and needs. The synchronous mode will be achieved by
providing an operator derived from `airflow.models.baseoperator.BaseOperator`, which
executes a Data Job and waits for its completion. The asynchronous mode will be achieved
by providing a sensor operator derived from `airflow.sensors.base.BaseSensorOperator`,
which polls on the specific time intervals for job execution completion and does not hold
the Airflow Worker.

* Availability.
    * The availability of the VDK Provider will be managed by Airflow, since it is going
      to be deployed as part of Airflow ecosystem.

* Capacity Estimation and Constraints TODO

<!--
* Capacity Estimation and Constraints
    * Cost of data path: CPU cost per-IO, memory footprint, network footprint.
    * Cost of control plane including cost of APIs, expected timeliness from layers
      above.

* Performance.
    * Consider performance of data operations for different types of workloads. Consider
      performance of control operations
    * Consider performance under steady state as well under various pathological
      scenarios, e.g., different failure cases, partitioning, recovery.
    * Performance scalability along different dimensions, e.g. #objects, network
      properties (latency, bandwidth), number of data jobs, processed/ingested data, etc.
* Telemetry and monitoring changes (new metrics).
* Configuration changes.
* Upgrade / Downgrade Strategy (especially if it might be breaking change).
* Troubleshooting
    * What are possible failure modes.
        * Detection: How can it be detected via metrics?
        * Mitigations: What can be done to stop the bleeding, especially for already
          running user workloads?
        * Diagnostics: What are the useful log messages and their required logging levels
          that could help debug the issue?
        * Testing: Are there any tests for failure mode? If not, describe why._
* Operability
    * What are the SLIs (Service Level Indicators) an operator can use to determine the
      health of the system.
    * What are the expected SLOs
* Test Plan
    * Unit tests are expected. But are end to end test necessary. Do we need to extend
      vdk-heartbeat ?
* Dependencies
    * On what services the feature depends on ? Are there new (external) dependencies
      added?
-->

#### VDK Hook

Airflow Hooks act as an interface for communication with the external shared resources in
a DAG. In our case, the VDKHook will encapsulate the logic for the communication with the
Control Service. It will provide methods for starting, canceling, and retrieving Data Job
executions. Also, it will contain a built-in HTTP client with configurable retry and
authentication mechanisms. The hook also will help to avoid storing connection
authentication parameters in a DAG by
using [Airflow Connections](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html)
.

In this way, the implemented logic can be reused in different operators
(e.g. VDKOperator and VDKSensorOperator). Such an approach provides better decoupling and
utilization of added integration.

#### VDK Operator

The extensibility is one of the many reasons which make Apache Airflow powerful. Airflow
allows us to create a custom operator that suits our requirements to communicate with
Control Service via Execution API.

VDKOperator is responsible for the **synchronous** execution of Data Jobs. It starts a
Data Job execution and waits for its completion. While it is waiting for the job
execution completion, it does not release the Airflow Worker. For that reason, it is not
recommended for long-running Data Jobs and `VDKSensorOperator` should be used instead.

It is defined by extending the `airflow.models.baseoperator.BaseOperator`,
defining `execute` and `on_kill` methods:

* Execute - It defines the code to be executed when the Airflow Runner calls the
  operator. Based on
  `asynchronous` variable (by default=False) which indicates whether the method should
  start a data job execution and wait for its completion or just start data job execution
  and return an execution id. The `asynchronous`=True is used in combination with
  VDKSensorOperator (more on that below).
* on_kill - This method cancels the Data Job execution when an Airflow task instance gets
  killed.

Usage:

```python
from airflow import DAG
from airflow.providers.vdk.operators.vdk import VDKOperator

with DAG:
   # [START sync_data_job]
   sync_data_job = VDKOperator(
      job_name='sync_data_job',
   )
   # [END sync_data_job]

   sync_data_job
```

#### VDK Sensor Operator

Airflow provides a primitive for a special kind of operator, whose purpose is to poll
some state (e.g. data job completion) at regular intervals until a success criterion is
met. Sensors have a powerful feature called 'reschedule' mode, which allows the Airflow
Scheduler to reschedule a sensor task, rather than blocking a worker slot between pokes.
This is useful when you can tolerate a longer poll interval and expect to be polling for
a long time.

VDKSensorOperator is responsible for the **asynchronous** execution of Data Jobs in
combination with VDKOperator. As the sensors only have the ability to poll the state of
data job execution, the VDKOperator has to be used to start it. The sensor is defined by
extending the airflow.sensors.base.BaseSensorOperator and defining a `poke` method to
poll Data Job execution state and evaluate the job execution completion.

Usage:

```python
from airflow import DAG
from airflow.providers.vdk.operators.vdk import VDKOperator
from airflow.providers.vdk.sensors.vdk import VDKSensorOperator

with DAG:
   # [START async_data_job]
   start_async_data_job = VDKOperator(
      job_name='async_data_job',
      asynchronous=True,
   )

   async_data_job = VDKSensorOperator(
      job_name='async_data_job',
      job_execution_id=start_async_data_job.output,
   )
   # [END async_data_job]

   async_data_job
```

#### Sample DAG

```python
from airflow import DAG
from airflow.providers.vdk.operators.vdk import VDKOperator
from airflow.providers.vdk.sensors.vdk import VDKSensorOperator

with DAG(
   dag_id='sample_vdk_dag',
   schedule_interval=None,
   start_date=datetime(2022, 3, 3),
   catchup=False,
   default_args={'team_name': 'default_team_name', 'conn_id': 'default_conn_id'},
) as dag:
   # [START sync_data_job]
   sync_data_job = VDKOperator(
      job_name='sync_data_job',
   )
   # [END sync_data_job]

   # [START async_data_job]
   start_async_data_job = VDKOperator(
      job_name='async_data_job',
      asynchronous=True,
   )

   async_data_job = VDKSensorOperator(
      job_name='async_data_job',
      job_execution_id=start_async_data_job.output,
   )
   # [END async_data_job]

   sync_data_job >> async_data_job
```

### Security and Permissions

The communication between VDK Provider and Control Service will be secured through the
use of HTTPS and OAuth 2.0. The most commonly used OAuth 2.0 flows will be supported (
e.g. Client Credentials Flow, Refresh Token Flow, etc.).

Secrets will be stored as part
of [Airflow Connection](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html)
like follows:

* Refresh Token Flow:

| Name             | Value             |
|------------------|-------------------|
| connection.login | Empty             |
| connection.password | Refresh/API token |

* Client Credentials Flow:

| Name                | Value         |
|---------------------|---------------|
| connection.login    | Client ID     |
| connection.password | Client Secret |

<!--
How is access control handled?
* Is encryption in transport supported and how is it implemented?
* What data is sensitive within these components? How is this data secured?
    * In-transit?
    * At rest?
    * Is it logged?
* What secrets are needed by the components? How are these secrets secured and attained?
-->

## Implementation stories

TODO
<!--
Optionally, describe what are the implementation stories (eventually we'd create github issues out of them).
-->

## Alternatives

TODO
<!--
Optionally, describe what alternatives has been considered.
Keep it short - if needed link to more detailed research document.
-->
