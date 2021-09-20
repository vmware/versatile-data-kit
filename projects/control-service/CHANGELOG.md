Changelog
=========

1.2.9 - Next
----
* **New feature**
  * Current Execution Logging API introduced (experimental).
    While users are executing remotely a data job they can monitor their logs now.s

* **Improvement**
  * GraphQL endpoint now does not have limit for fetching data jobs, which was previously 100 jobs per page.

* **Bug Fixes**
  * Data job execution status fix
    In case of failed data job execution due to the User Error the execution status will be marked as Failed instead of Finished.

  * Data Job Execution statuses synchronization
    This will keep in sync all job executions in the database in case of Control Service downtime or missed Kubernetes Job Event.

* **Breaking Changes**
  * Removed '-latest' suffix from the К8S Cron Job name


1.2.7 - 03.09.2021
----
* **Improvement**
  * Extra arguments can be passed to the data job builder via the DATAJOBS_DEPLOYMENT_BUILDER_EXTRAARGS environment variable
  * The name of the user who has triggered manual job executions is now displayed
  * It is now possible to connect to insecure Git repositories by using the GIT_SSL_ENABLED environment variable


1.2.6 - 31.08.2021
----

* **New feature**
  * Adding support for forwarding logs of the Control Service Server (only) to syslog server <br>
    Users can now specify environment variable LOGGING_SYS_LOG_HOST and LOGGING_SYS_LOG_PORT to enable forwarding them to syslog.


1.2.5 - 30.08.2021
----

* **New feature**
  * implement DELETE Job execution REST API<br>
    Users can now cancel started data job execution in self-service manner using REST API


* **Improvement**
  * Switch Job Builder image to use kaniko<br>
    This will enable Control Servie to run in more secure kubernetes (pod security - no privilege run, seccomp/apparmor profiles enabled)
    It will enable to use local docker registry (without ssl) for easier deployment for prototype purposes

* **Bug Fixes**

* **Breaking Changes**


1.2.4 - 27.08.2021
---
* **New feature**

* **Improvement**

* **Bug Fixes**
  * Non-accurate control-service image tag fix
  * Data Job deployment fix
    Fixed data jobs deployment failures that emit 'ERROR: restart transaction' due to DeploymentMonitor.recordDeploymentStatus.

* **Breaking Changes**


1.2.2 - 19.08.2021
----

* **New feature**

* **Improvement**
  * Expose data job base image as configuration
    Data job base image used to run deployed data job can be configured using helm now.

* **Bug Fixes**
  * Generating javadoc fix

* **Breaking Changes**


1.2.1 - 18.08.2021
----

* **New feature**

* **Improvement**
  * Make the image registry in the helm chart configurable.
    Configure registry part of docker images used for control-service API, job builder image and VDK distribution image.
    This make it easier to use docker cache proxies.

* **Bug Fixes**

* **Breaking Changes**


1.2.0 - 17.08.2021
----
Initial release of Control Service in the public VDK Helm repository.

* **New feature**
  - Data Job Management REST API
    - Create, configure, delete Data Jobs
    - Download keytab to run job locally against Data Plane
    - Automatically provision of kerberos users for each Data Job
  - Data Jobs Deployment REST API
    - Upgrade of SDK can happen across all jobs in minutes
    - Job Notification in case of User or Platform issues
    - Enable and Disable Data Job Deployment
  - Admins can set VDK options globally or per job - set as environment variable during VDK execution in cloud.
  - REST API exposes Prometheus monitoring metrics`
  - Helm installation in Kubernetes compatible with VMware Tanzu Application Catalog (Bitnami).
  - Support for AWC ECR Docker Registry (Data Jobs images stored there)
  - Deploying job directly through the API only (Upload endpoint added in REST API)
  - Authentication/Authorization using Oauth2
    - Bearer Access Token Support
    - Authorization decision using HTTP WebHook
  - Add support for generic (Harbor/Dockerhub) docker registry
  - Support for external database configuration
  - Add new GraphQL API Endpoint for listing Data Jobs. See the swagger doc for more information.
  - Data job termination status monitoring, configurable through the datajobs.status.watch.interval and datajobs.status.watch.initial.delay properties.
  - Allow enabling/disabling of per-execution notifications via enable_execution_notifications in the data job's config.ini.
  - GET Sources API implementation
  - Configurable data job template can be provided via Helm
  - Data Job Execution API that allows clients to execute their jobs remotely.

* **Improvement**

* **Bug Fixes**

* **Breaking Changes**
