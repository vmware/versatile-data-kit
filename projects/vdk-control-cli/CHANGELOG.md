Changelog
=========

VDK Control CLI 1.1 - (not yet)
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
