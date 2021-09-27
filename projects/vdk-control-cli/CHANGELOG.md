Changelog
=========

VDK Control CLI 1.1
------
* **New feature**

* **Improvement**
    * vdk create to handle cases without control service better:
      Introduced vdk create --local to create job only locally from sample
      vdk create without arguments would create job locally and try to detect if it can created in cloud
      vdk create --cloud - always created in cloud only and fail if it cannot
    * Auto-detect if authentication is necessary
      This remove the need of explicit variable to set/unset authentication. Now vdkcli would detect automatically.

* **Bug Fixes**

* **Breaking changes**


VDK Control CLI 1.0 - (10.08.2021)
------

First release of VDK Control CLI.
The CLI aims to help engineers develop, create, manage, deploy Data Jobs

* **New feature**
  - Data Job Management CLI
    - Create, delete, deploy Data Jobs
    - vdk download-job enables downloading a data job source directory locally.
    - vdk properties command line tool enabling user to manage their data job properties using CLI only.
    - vdk show - show all details for a single job - will be used for debugging purposes - meant for operators/developers for now.
    - vdk set-default - to set default team
 - OAuth2 Authentication support
    - Supports login using API Token or Authorization Code Grant flow
  - Plugin mechanism for easily extending the SDK.
    - Hook for specifying default options for CLI arguments


* **Improvement**

* **Bug Fixes**

* **Breaking changes**
