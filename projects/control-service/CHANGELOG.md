Changelog
=========

1.2.2 - Next
----


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
