
# VEP-NNNN: Your short, descriptive title

* **Author(s):** Paul Murphy (murphp15@tcd.ie),Iva Koleva (ikoleva@vmware.com)
* **Status:** implementable

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
Create an open source frontend for the VDK.  
The frontend will let customers, create,delete deploy and generally managed nad browse their jobs.
For frontend is written in an extensible format to easily allow other teams to build extensions.

## Glossary
data-pipelines: This is the npm project of the bootstrapping codebase it contains all the vdk specific frontend code 
shared-components, @vdk/shared: This is a set of components that are used within the data-pipelines project but are generic and could be re-used by other projects 

## Motivation
1. Improve usability
   1. With a UI customers will be able to use VDK much quicker and much more proficiently because UIs are easier to understand and become familiar with than CLI tools
2. increase VDK adoption 
   1. At the moment the VDK needs to be interacted with through the VDK cli or through web requests. Its thought that this is slowing down adoption of the VDK.

## Requirements and goals

1. website should be intuitive, fast, responsive
2. It should be easy to setup and run locally
3. It should be easy to extend with new features
4. It should be well tested
5. It should be well documented

## High-level design

#### Folder Structure

* [frontend-ui](../../projects/frontend-ui) The root folder for all frontend code.
  * [shared](../../projects/frontend-ui/shared/README.md): the root folder for the shared components project, for more details please see the readme.
  * [data-pipelines](../../projects/frontend-ui/data-pipelines/README.md): the root folder for the data-pipelines project, for more details please see the readme.

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


## Implementation stories
<!--
Optionally, describe what are the implementation stories (eventually we'd create github issues out of them).
-->

## Alternatives
<!--
Optionally, describe what alternatives has been considered.
Keep it short - if needed link to more detailed research document.
-->
