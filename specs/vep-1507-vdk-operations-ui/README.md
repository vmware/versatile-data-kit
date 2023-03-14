
# VEP-NNNN: Your short, descriptive title

* **Author(s):** Paul Murphy (murphp15@tcd.ie), Iva Koleva (ikoleva@vmware.com), Dilyan Marinov (mdilyan@vmware.com)
* **Status:** implemented

- [VEP-NNNN: Your short, descriptive title](#vep-nnnn-your-short-descriptive-title)
  - [Summary](#summary)
  - [Glossary](#glossary)
  - [Motivation](#motivation)
  - [Requirements and goals](#requirements-and-goals)
    - [Goals:](#goals)
    - [Non Goals:](#non-goals)
  - [High-level design](#high-level-design)
      - [Folder Structure](#folder-structure)
      - [Package publishing](#package-publishing)
  - [Detailed design](#detailed-design)
    - [CI/CD](#cicd)
      - [Dependency management](#dependency-management)
      - [Build and Test](#build-and-test)
        - [e2e test image](#e2e-test-image)
      - [Release](#release)
  - [Implementation stories](#implementation-stories)

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
shared-components, @versatiledatakit/shared: This is a set of components that are used within the data-pipelines project but are generic and could be re-used by other projects [README.md](/projects/frontend/data-pipelines/README.md)

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
The shared components and data-pipelines packages are published to the [npm
registry](https://www.npmjs.com/) under the user
[@verstiledatakit](https://www.npmjs.com/settings/versatiledatakit/packages).
The npm registry was chosen as the package repository because it is the most
widely adopted javascript package manager. Publishing to the registry also
supports the following workflows:
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
### CI/CD

CI/CD for frontend components leverages existing CI/CD for the VDK monorepo using
GitLab.

- [GitLab config for frontend components](/projects/frontend/cicd/.gitlab-ci.yml)
- [@versatiledatakit/shared install script](/projects/frontend/cicd/install_shared.sh)
- [@versatiledatakit/data-pipelines build script](/projects/frontend/cicd/build_data_pipelines.sh)
- [@versatiledatakit/data-pipelines install script](/projects/frontend/cicd/install_data_pipelines.sh)
- [release script for npm packages](/projects/frontend/cicd/publish_package_npm.sh)

The shells scripts linked above are designed for CI/CD and local development use.

#### Dependency management

Our main goals when it comes to dependency management are as follows:

1. Keep peer dependencies up to date to avoid vulnerabilities
2. Detect problems related to peer dependencies early

Therefore, peer dependency versions are lower-bound, i.e. the version of a specific peer
dependency should be greater than or equal to a specific number. Peer dependency
versions should not be upper-bound unless absolutely necessary.

`package-lock.json` is not included in version control for either package.
Instead, for each pipeline run, `npm install` is run and `package-lock.json` is
output as an artefact at the end. Artefact retention is 7 days. This setup
ensures that the latest dependencies are pulled for every build. It also ensures
compatibility issues are detected early and are traceable.

**Advantages of using lower-bound peer dependency versions**

1. Reduces conflicts. Setting a lower-bound version for a peer dependency
ensures that the package uses a compatible version of that dependency and
reduces the chance of conflicts (if another version is pinned somewhere else).
It also provides more flexibility to users: they can pin the version themselves
if they have to.

2. Improves security. Ensures we use the latest versions and makes it easier to
keep up with updates.

**Disadvantages** Compatibility issues. If a new version of a dependency
introduces a breaking change, this leads to increased maintenance, due to
failures in CICD.

**Alternatives considered**

Pinned dependencies and Dependabot automatic updates. The dependencies are
pinned and dependabot automatically updates them. This keeps peer dependencies
up to date and allows the detection of problems early by opening PRs after a new
dependecy release. The disadvantage here is that the process becomes too
granular, e.g. every peer dependency update opens a new PR, which triggers a new
release.

Range-based dependencies. Specify only major version and allow any minor and
patch version to be used. Dependabot opens PRs only for major version updates.
This is better in terms of granularity, but reduces flexibility.

#### Build and Test

Opening a pull request with changes to `@versatiledatakit/data-pipelines`
triggers a pipeline that builds the shared package and runs unit tests on it.
Opening a pull request with changes to `@versatiledatakit/shared` triggers a
pipeline that builds and tests both the data-pipelines and shared packages to
ensure compatibility. Opening a pull request with changes to the [frontend CI/CD](/projects/frontend/cicd)
triggers a pipeline that builds and tests both packages. Merging changes into
`main` requires that these pipelines pass successfully.

##### e2e test image
To run e2e tests a lot of dependencies are needed (browsers, build systems etc...).
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

**Related Issues**
https://github.com/vmware/versatile-data-kit/issues/1728

#### Release

Frontend packages are published under the
[@verstiledatakit](https://www.npmjs.com/settings/versatiledatakit/packages)
namespace in npm registry. Merging changes to a package triggers the publishing
of that package to npm. Frontend packages are **not** included in VDK nightly
builds. This setup ensures that each atomic change to the frontend corresponds
to a release version.

Versioning for each package is based on its `version.txt` file and the gitlab
pipeline id. Major and minor versions are taken from `version.txt`. The gitlab
pipeline id, which is guaranteed to be unique, serves as the patch version. Note
that `package.json` files do not represent package versions and should not be
used as a source of truth for versioning.

- [version.txt for @versatiledatakit/data-pipelines](/projects/frontend/data-pipelines/gui/version.txt)
- [version.txt for @versatiledatakit/shared](/projects/frontend/shared-components/gui/version.txt)

As stated in [CONTRIBUTING.md](/CONTRIBUTING.md), versioning of all components follows https://semver.org

## Implementation stories
<!--
Optionally, describe what are the implementation stories (eventually we'd create github issues out of them).
-->
