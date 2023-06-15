

# Goals

The main goal of the Versatile Data Kit is to enable efficient data engineering.

* **Simplifying data development & data engineering:** VDK aims to provide a simpler, more flexible approach to the development of data that reduces the amount of boilerplate code that data engineers have to write.
* **Adopt and adapt good software development practices:** VDK aims to establish and implement good software development and engineering practices, such as, testing, separation of concerns, loose coupling, versioning, code/config separation which make code and datasets more maintainable and testable
* **Promoting good data engineering practices:** VDK aims to encourage best practices in data engineering, such as providing automated error handling, support for quality, and validation, and making it easy to reuse data modeling techniques.
* **Use only what you need - modular and extensible:** VDK aims to enable users to choose to use only the specific functionalities or modules they need and nothing more. And developers can extend the framework with new functionalities as the data ecosystem evolves.

# Architecture

## System Context Diagrams

Versatile Data Kit is conceptually composed of two independently usable components:
- Control Service
- Python-based SDK.


The Control Service provides all the horizontal components required to configure and run [data jobs](https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job) on any cloud: the UI, and REST APIs for deployment, execution, properties and secrets. Also job scheduling, logging, alerting, monitoring etc. It is tightly coupled with Kubernetes and relies on Kubernetes ecosystem for many of its functionalities.

![VDK Control Service System Context Diagram](https://github.com/vmware/versatile-data-kit/assets/2536458/84da99c8-2d2d-44d9-90a8-f0ea6ae5150f)


<br><br>

The VDK SDK consists of all user tools that assist in developing data jobs focusing on data ingestion and transformation.
It can be installed locally on the user's machine to enable a local development experience.
It follows plugin-oriented architecture where all functionality is built through plugins which enables reconstructing VDK SDK in any flavor depending on the organization's and users' needs.

![VDK SDK System Context Diagram](https://github.com/vmware/versatile-data-kit/assets/2536458/8fab24c9-5d22-4f83-a41f-1a025f2edb4a)

## VDK Control Service Container Diagram

![VDK Control Service Container Diagram](https://github.com/vmware/versatile-data-kit/assets/2536458/89312655-7171-432a-8147-551dd2d711ea)

Diving deeper into the VDK Control Service, the entry point from data practitioner's perspective is
* VDK Frontend UI which is used for operating and monitoring of data jobs.
* [VDK Rest API](https://iaclqhm5xk.execute-api.us-west-1.amazonaws.com/data-jobs/swagger-ui/index.html#/) (through VDK Control CLI or Notebook UI) which is used to deploy and configure data jobs.

From operator's perspective:
* Operators use provided [helm chart](https://github.com/vmware/versatile-data-kit/wiki/Installation#install-versatile-data-kit-control-service) to install, and configure the Control Service deployment and the needed data infrastructure.

#### Rest API

[Control Service Rest API](https://iaclqhm5xk.execute-api.us-west-1.amazonaws.com/data-jobs/swagger-ui/index.html) reflects the usual Development lifecycle:
- Create a new data job when starting on a new use case.
- Develop, run, and test the data job locally.
- Deploy the data job in a cloud runtime environment to run on a scheduled basis with monitoring and alerting in case of issues.

The Rest API is implemented in Java with Spring Boot framework to take advantage of Java's huge ecosystem of libraries. With a few lines of configuration, Spring Boot bootstraps a service with a complete toolchain included but not limited to advanced logging and metrics reporting, declarative persistence and full [REST API with Swagger UI](https://iaclqhm5xk.execute-api.us-west-1.amazonaws.com/data-jobs/swagger-ui/index.html). Operators can also configure VDK Control Service to use existing Logging and Monitoring system in organization ecosystem.
The REST API provides Oauth2 based authentication and authorization and authorization can be extended with authorization webhook.

#### VDK Frontend UI
VDK Frontend UI is an Angular-based web application. It relies on VDK Rest API and especially for almost all read operations on the [Rest GraphQL Query API](https://iaclqhm5xk.execute-api.us-west-1.amazonaws.com/data-jobs/swagger-ui/index.html#/Data%20Jobs/jobsQuery) .

#### Builder Job
Builder Jobs are used to build and release users' data jobs. Those are system jobs used during deployment to install all dependencies and package the data job. Builder Jobs interacts with Git to read the source code and with Container Registry (e.g. Docker) in order to store the data job image. Operators can provide custom a builder image with further capabilities (for example running system tests to verify data jobs , security hardening like checking for malicious code, etc.)

#### Data Job

The deployment of a data job happens as a CronJob deployment in Kubernetes. CronJob pulls the data job image from the Container Registry upon each execution. The data jobs are run in Kubernetes and monitored in cloud runtime environment via Prometheus, which uses the Kubernetes APIs to read metrics.

#### Database

CockroachDB is used to store the data job metadata. This includes information about data job definitions, and data job executions.

## VDK SDK Component Diagram

![VDK SDK Component Diagram](https://github.com/vmware/versatile-data-kit/assets/2536458/be8d805d-0026-4e0b-afeb-32d72b98f70d)

Diving deeper into the VDK SDK, the entry point from the data practitioner's perspective is
* VDK Data Job Framework which provides tools and interfaces to perform ETL operations on data through SQL or Python.

Operators and data practitioners can use VDK Plugin Framework to customize and extend VDK.

#### vdk-core

The core component of VDK contains the Data Job Framework and the Plugin Framework.

##### Data Job Framework

Data Job Framework which gives the users the ability to access different data development interfaces.

Users create [data jobs](https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job). Each data job can contain multiple [steps](https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job-step) executed in alphanumeric order by default (this can be customized). vdk run is used to run a full data job both locally and when deployed in the cloud. Users can install plugins like vdk-notebook that provide IDE for building jobs as well.
[Job Input](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py) provides different capabilities for ingesting data, transforming data with templates, accessing properties and secrets, etc.

##### Plugin Framework

The plugin Framework exposes many different types of hooks that can be attached for database-managed connection (e.g. ingest and query impala data in vdk-impala), vdk commands customization (e.g. vdk-control-cli), any phase of data job execution (e.g. add new steps in vdk-notebook plugin) or Data Job Framework improvements (e.g. vdk-lineage).

See more details in [here](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins#plugins).
