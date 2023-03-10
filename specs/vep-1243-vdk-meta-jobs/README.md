
# VEP-1243: VDK Meta jobs

* **Author(s):** Yoan Salambashev (ysalambashev@vmware.com)
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

<!--
Short summary of the proposal. It will be used as user-focused
documentation such as release notes or a (customer facing) development roadmap.
The tone and content of the `Summary` section should be
useful for a wide audience.
-->

The Meta Job is a new feature in VDK that enables users to manage job dependencies in their data processing workflows.
It allows a Data Job to manage other Data Jobs by triggering them on certain job completion conditions (i.e. job1
and job2 complete before job3 starts) resulting in more accurate and consistent data output. An integration with
Apache Airflow is available, but it requires users to manage their own instance or pay for an externally managed
service. Meta Jobs provide a more lightweight alternative that simplifies the process and reduces cost.

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

Data teams are constantly looking for ways to optimize and streamline their data processing workflows.
One critical aspect of these workflows is managing job dependencies, which ensures that Data Jobs are executed
in the appropriate order. Until now, we addressed this problem
by integrating with the external tool Apache Airflow. However, this approach comes with its downsides: teams would
have to manage their instance of Airflow or pay for an externally managed service.

To address this problem, VDK is introducing the Meta Jobs plugin. Meta Jobs are providing users with the ability
to manage job dependencies natively within the framework. They ensure that one or more Data Jobs will be triggered
upon successful completion (or other specified criteria) of one or more other Data Jobs. Similarly to other
orchestrating services, Meta Jobs express the dependencies as a DAG. As Data Jobs themselves, they go with
all the powerful features as every other Data Job, such as scheduling and monitoring.
This new feature gives users the ability to easily orchestrate the workflow the way they want it.

Meta Jobs allow for greater job segmentation, which can prove beneficial when working with complex
pipelines. Breaking down the pipelines into more manageable Data Jobs can help users with maintaining and debugging.
Thus, this feature will save time, resources, and worries about external dependencies.
Our data engineering framework empowers data teams to manage job dependencies with control, leading to more
reliable and efficient data processing workflows.

## Requirements and goals
<!--
It tells **what** is it trying to achieve?
List the specific goals (functional and nonfunctional requirements)? How will we
know that this has succeeded?

Specify non-goals. Clearly, the list of non-goals can't be exhaustive.
Non-goals are only features, which a contributor can reasonably assume were a goal.
One example is features that were cut during scoping.
-->

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

Although having all these pros, the user should have in mind the cons of the Meta Jobs as well. The limitation that
have to be considered is that there is a limit on the number of concurrent running jobs in a single DAG. If this
limit is exceeded, the upcoming jobs would be delayed for a while until there is an empty spot for them.

## Implementation stories
<!--
Optionally, describe what are the implementation stories (eventually we'd create github issues out of them).
-->

## Alternatives
<!--
Optionally, describe what alternatives has been considered.
Keep it short - if needed link to more detailed research document.
-->
