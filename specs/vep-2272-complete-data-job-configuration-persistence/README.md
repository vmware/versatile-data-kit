# VEP-2272: Complete Data Job Configuration Persistence

* **Author(s):** Miroslav Ivanov (miroslavi@vmware.com)
* **Status:** draft

- [Summary](#summary)
- [Glossary](#glossary)
- [Motivation](#motivation)
- [Requirements and goals](#requirements-and-goals)
- [High-level design](#high-level-design)
- [API Design](#api-design)
- [Detailed design](#detailed-design)
- [Implementation stories](#implementation-stories)
- [Alternatives](#alternatives)

## Summary

Currently, the deployment configuration of data jobs is partially dependent on the Kubernetes cluster, leading to
unnecessary overhead when loading data job deployments. Additionally, the loss of Kubernetes namespace results in the
potential loss of data jobs, requiring a manual and complex restoration process. By switching the source of truth from
Kubernetes to a database, we can ensure a more reliable and easy restoration process while optimizing performance for
Control Service APIs.

## Glossary

* VDK: https://github.com/vmware/versatile-data-kit/wiki/dictionary#vdk
* Control Service: https://github.com/vmware/versatile-data-kit/wiki/dictionary#control-service
* Data Job: https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job
* Data Job Deployment: https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job-deployment
* Kubernetes: https://kubernetes.io/

## Motivation

Ensuring efficient and reliable management of data job deployments is crucial for the smooth functioning of our system.
Currently, when a data job is deployed, its deployment configuration is stored in both Kubernetes and the database.
However, there exists a disparity where certain essential properties are exclusively stored in Kubernetes, such as the
job's enabled status, Python version, and deployment information.

This discrepancy creates a significant challenge for the Control Service APIs that rely on retrieving data job
deployments. For instance, the GraphQL API's jobs query initially retrieves the data jobs from the database and
subsequently retrieves the deployment data from Kubernetes. This two-step process introduces performance degradation to
the Control Service, as it requires additional time and resources to fetch information from multiple sources.

Moreover, in the event of a Kubernetes namespace loss, there is a potential risk of losing critical data job deployment
configurations. In such scenarios, recovering the lost data jobs becomes a manual and complex restoration process.
This adds further complexity and potential downtime for users relying on the Control Service for their data job
management needs.

To address these issues, it is essential to optimize the storage and retrieval of data job deployments. By ensuring that
all relevant properties are stored consistently, in the database, so we can streamline the process and enhance the
overall the efficiency of the Control Service APIs.

By improving the efficiency and reliability of data job deployments, we aim to optimize the overall system performance
and provide a seamless experience for our users.

## Requirements and goals

### Goals

1. Identify the specific data job configuration that is stored only within the Kubernetes cluster.
2. Transition the primary source of truth for all data jobs configurations from both Kubernetes and database to just the
   database, in order to centralize data storage, improve data integrity, and enable easier access and manipulation.
3. Enhance the performance of Control Service APIs by loading the data job configuration from only one data source
   (Control Service database).
4. Prepare Control Service for future enhancement of the migration process and ease of restoration by centralizing and
   storing all data job configurations within the database.

### Non-Goals

1. Implement automatic data jobs restore capability in case of the loss of Kubernetes namespace whereby the Control
   Service automatically retrieves the configuration from a database and seamlessly restores the data jobs.

## High-level design

These diagrams below show a high-level design view of the changes that would be proposed in this VEP.

|                       Deploy Data Job                       |                           Read Data Job Deployment Configurations                           |
|:-----------------------------------------------------------:|:-------------------------------------------------------------------------------------------:|
| ![deploy_data_job_diagram.png](deploy_data_job_diagram.png) | ![read_data_job_deployment_config_diagram.png](read_data_job_deployment_config_diagram.png) |

The proposed design will introduce changes to the Control Service (deployment logic, GraphQL API, etc.), as well as to
the database model.

When the Control Service receives an API call to deploy data job, it will store the complete deployment configuration in
both Kubernetes and the database. However, when it receives an API call to retrieve the data job deployment
configuration, it will only query the database.

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
