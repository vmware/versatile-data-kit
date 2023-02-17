
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

<!--
Short summary of the proposal. It will be used as user-focused
documentation such as release notes or a (customer facing) development roadmap.
The tone and content of the `Summary` section should be
useful for a wide audience.
-->

At the moment customers can deploy and manage jobs through the VDK CLI tool or through the API's.
We want to extend on this and create a web frontend for the VDK.
The frontend will let customers, create,delete deploy and generally manage and browse their jobs.
Frontend is written in an extensible format to easily allow other teams to build extensions.
To achieve this extensibility the frontend is built in angular.

## Glossary
<!--
Optional section which defines terms and abbreviations used in the rest of the document.
-->

data-pipelines: This is the npm project of the bootstrapping codebase it contains all the vdk specific frontend code. for more details please see [README.md](/projects/frontend/data-pipelines/README.md)
shared-components, @vdk/shared: This is a set of components that are used within the data-pipelines project but are generic and could be re-used by other projects [README.md](/projects/frontend/data-pipelines/README.md)

## Motivation
One of the core goals of the VDK is to provide a common and efficient framework for implementing, executing, monitoring, and troubleshooting data jobs (and data pipelines).

In a sufficiently complex system, a single data team would need to manage many different data jobs - upgrade them, monitor them, fix incidents and issues, etc. Using CLI or API directly for the purpose of troubleshooting or operating multiple jobs doesn't scale. The CLI is very limited in terms of filtering, searching and visualizing complex information. And both require a higher level of technical skills to use.

In an UI we want user to be able to

For Developers - To be able to manage data jobs that allows for more flexibility - update configuration, check latest version, etc.
For Operator/Support - ability to detect status of data jobs and easily access troubleshooting tools, as well as the ability to track and see log data jobs
For team leads to be able to have aggregated view of the status of all jobs how often they fail, why do they fail.


## Requirements and goals
<!--
It tells **why** do we need X?
Describe why the change is important and the benefits to users.
Explain the user problem that need to be solved.
-->

### Goals:
1. It should be easy to setup and run locally or in a k8s cluster.
2. It should be easy to extend with new features
   1. Adding a new section should be well documented
   2. We expect programmers who didn't work on the initial build of the project to be able to build a section for their needs in isolated manner
   3. After they have created a section they can easily add it to a deployed instance



### Non Goals:
1. Screens for rendering data lineage graphs.

## High-level design

#### Folder Structure

* [frontend](/projects/frontend) The root folder for all frontend code.
    * [shared-components](/projects/frontend/shared-components/README.md): the root folder for the shared components project, for more details please see the readme.
      * gui: This contains the root package.json file for the project.
        * projects:
          * documentation-ui: functionality for testing and developing new components
          * shared: all the shared components live here
      * cicd: gitlab config
    * [data-pipelines](/projects/frontend/data-pipelines/README.md): the root folder for the data-pipelines project, for more details please see the readme.
    * cicd: contains docker images, scripts etc needed for cicd jobs
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
#### Package publishing
The shared-component and frontend packages are published to NPMJS(https://www.npmjs.com/) under the user versatiledatakit.
NPMJS was chosen as the package repository because it is the most widely adopted javascript package manager.
They are published to a public NPMJS to support two workflows:
1. Customers want to use the shared component libraries in their projects.
2. Customers want to build their own docker image for data-pipelines instead of using the one provided by us.



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
### CICD

#### e2e test image
To run e2e tests alot of dependencies are needed (browsers, build systems etc...).
Cypress(e2e framework) are actually aware of this and provide a base image.
We extend this with extra functionality we need.
A docker image is built with all these dependencies to make e2e testing easier in gitlab.

it contains:
1. Angluar (build)
2. Chrome Browser (for UI testing)
3. Command cli utils (curl, git, zip etc...) (auxiliary functions/packaging reports etc..)
4. Sonar (Code Quality checking)
5. Npm and Nvm (build)

The actual dockerfile can be found at [Dockerfile](/projects/frontend/cicd/Dockerfile)
New versions are released by changing the version in [version.txt](/projects/frontend/cicd/version.txt)
New releases are published under the image name [registry.hub.docker.com/versatiledatakit/vdk-cicd-base-gui](https://hub.docker.com/r/versatiledatakit/vdk-cicd-base-gui)

## Implementation stories
<!--
Optionally, describe what are the implementation stories (eventually we'd create github issues out of them).
-->
