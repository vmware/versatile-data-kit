Changelog
=========

ChangeLog is no longer updated.
Release notes are generated automatically through [VDK release process](https://github.com/vmware/versatile-data-kit/blob/main/CONTRIBUTING.md#how-to-make-a-new-vdk-release)

The file is kept for historical purposes to show the evolution of the Control Service before release process was in place.

1.3 - 09.03.2022
----
* **Improvement**
  * Security improvement. Use empty dir storage for storing jobs during upload/deployment/etc instead of using the root file system

1.3 - 09.03.2022
----
* **Improvement**
  * Adopted kubernetes-client 13.0

* **Bug Fixes**
  * Fix log link to always set endTime

1.3 - 18.02.2022
----
* **Improvement**
  * Support rootless data job deployment container images and builder jobs

1.3 - 27.01.2022
----
* **Improvement**
  * Publish Swagger UI to /data-jobs path<br>
    That is consistent with REST API paths.


1.3 - 20.12.2021
----
* **Improvement**
  * Add tracking and automatic release of locks on service shutdown<br>
    This will prevent delays in the K8s watching functionality on service restart/redeploy.


1.3 - 09.11.2021
----
* **Bug fixes**
  * Classify K8s pod OOM errors as UserError.

* **Improvement**
  * Users can now set vdk version (vdk image tag in reality)
    This would enable canary release of vdk, A/B testing.
    https://github.com/vmware/versatile-data-kit/issues/377


1.3 - 03.11.2021
----
* **Bug fixes**
  * Remove debug mode for data job build and release script.


1.3 - 02.11.2021
----
* **Bug fixes**
  * Remove logging of credentials in builder jobs.


1.3 - 2.11.2021
----
* **Improvement**
  * Reduce the default maximum duration of a data job execution to 12 hours


1.3 - 22.10.2021
----
* **Bug fixes**
  * Proper classification of data job requirements.txt errors


1.3 - 26.10.2021
----
* **Bug fixes**
  * Job executions that are terminated due to timeout are now classified as User Error.


1.3 - 25.10.2021
----
* **Improvement**
  * Add Kubernetes namespace as label to notification alerts.


1.3 - 21.10.2021
----
* **Bug fixes**
  * Clean up metrics when data jobs are deleted.


1.3 - 08.10.2021
----
* **Improvement**
  * Switch to a new versioning model where the patch version is automatically generated.
  * Control Service is now automatically released on every PR merge.


1.2.16 - 05.10.2021
----
* **Improvement**
  * Additional deployment labels are now set using valid YAML instead of a multiline string.


1.2.14 - 04.10.2021
----
* **Improvement**
  * Custom labels can now be supplied to the Control Service deployment during Helm chart installation.

* **Bug Fixes**
  * Fix an error which happens occasionally when listing data jobs or job deployment statuses


1.2.13 - 30.09.2021
----
* **Improvement**
  * Implement a new OAuth2 claim/role-based authorization model, which can work instead or in complement
    of the existing webhook-based authorization.


1.2.12 - 29.09.2021
----
* **New feature**
  * JSON-formatted logging is available via the LOGGING_FORMAT=JSON environment variable.

* **Improvement**
  * The Data Job Execution statuses synchronization takes into account SUBMITTED status.


1.2.11 - 27.09.2021
----
* **Bug Fixes**
  * Fixed helm chart to give correct permission to read logs
    This would fix Logging API to work and should fix the deployment notification on user error which was not sending notifications


1.2.10 - 23.09.2021
----
* **New feature**
  * Current Execution Logging API introduced (experimental).
    While users are executing remotely a data job they can monitor their logs now.


1.2.9 - 21.09.2021
----
* **Improvement**
  * GraphQL endpoint now does not have limit for fetching data jobs, which was previously 100 jobs per page.

* **Bug Fixes**
  * Data job execution status fix <br>
    In case of failed data job execution due to the User Error the execution status will be marked as Failed instead of Finished.

  * Data Job Execution statuses synchronization <br>
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
    This will enable Control Service to run in more secure kubernetes (pod security - no privilege run, seccomp/apparmor profiles enabled)
    It will enable to use local docker registry (without ssl) for easier deployment for prototype purposes


1.2.4 - 27.08.2021
---
* **Bug Fixes**
  * Non-accurate control-service image tag fix
  * Data Job deployment fix
    Fixed data jobs deployment failures that emit 'ERROR: restart transaction' due to DeploymentMonitor.recordDeploymentStatus.


1.2.2 - 19.08.2021
----
* **Improvement**
  * Expose data job base image as configuration
    Data job base image used to run deployed data job can be configured using helm now.

* **Bug Fixes**
  * Generating javadoc fix


1.2.1 - 18.08.2021
----
* **Improvement**
  * Make the image registry in the helm chart configurable.
    Configure registry part of docker images used for control-service API, job builder image and VDK distribution image.
    This make it easier to use docker cache proxies.


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
