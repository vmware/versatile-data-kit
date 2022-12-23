![Versatile Data Kit](./support/images/versatile-data-kit-xmass.svg#gh-light-mode-only)
![Versatile Data Kit](./support/images/versatile-data-kit-xmass.svg#gh-dark-mode-only)

<p align="center">
    <a href="https://github.com/vmware/versatile-data-kit/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/vmware/versatile-data-kit" /></a>
    <a href="https://github.com/vmware/versatile-data-kit/contributors" alt="Last Activity">
        <img src="https://img.shields.io/github/last-commit/vmware/versatile-data-kit" alt="Last Activity"></a>
    <a href="https://github.com/vmware/versatile-data-kit/blob/main/LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/vmware/versatile-data-kit" alt="license"></a>
    <a href="https://github.com/pre-commit/pre-commit">
        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="pre-commit"></a>
    <a href="https://github.com/vmware/versatile-data-kit">
        <img src="https://gitlab.com/vmware-analytics/versatile-data-kit/badges/main/pipeline.svg" alt="build status"></a>
    <a href="https://twitter.com/intent/tweet?text=Wow: @VDKProject">
        <img src="https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2FVDKProject" alt="twitter"/></a>
     <a href="https://www.youtube.com/channel/UCasf2Q7X8nF7S4VEmcTHJ0Q">
        <img alt="YouTube Channel Subscribers" src="https://img.shields.io/youtube/channel/subscribers/UCasf2Q7X8nF7S4VEmcTHJ0Q?style=social"></a>

<!-- TODO: code coverage -->
</p>

# Overview

Versatile Data Kit (VDK) is an open source framework that enables anyone with basic SQL or Python knowledge to build their own data pipelines.

Versatile Data Kit enables Data Engineers to develop, deploy, run and manage Data Jobs. **A Data Job is a data processing workload** and can be written in Python, SQL, or both at the same time. A Data Job enables Data Engineers to implement automated pull ingestion (E in ELT) and batch data transformation (T in ELT) into a database or any type of data storage.

![Without / With Versatile Data Kit](./support/images/versatile-data-kit-before-after-light.svg#gh-light-mode-only)
![Without / With Versatile Data Kit](./support/images/versatile-data-kit-before-after-dark.svg#gh-dark-mode-only)

Versatile Data Kit consists of two main components:

* A **Data SDK** provides all tools for the automation of data extraction, transformation, and loading, as well as a plugin framework that allows users to extend the framework according to their specific requirements.
* A **Control Service** allows users to create, deploy, manage and execute Data Jobs in Kubernetes runtime environment.

To help solve common data engineering problems Versatile Data Kit:
* allows ingestion of data from different sources, including CSV files, JSON objects, data provided by REST API services, etc.;
* ensures data applications are packaged, versioned, and deployed correctly while dealing with credentials, retries, reconnects, etc.;
* provides built-in monitoring and smart notification capabilities;
* tracks both code and data modifications and the relations between them, enabling engineers to troubleshoot faster and providing an easy revert to a stable version.


#### Data Journey and where VDK fits in
![Data Journey](./support/images/versatile-data-kit-data-journey.svg#gh-light-mode-only)
![Data Journey](./support/images/versatile-data-kit-data-journey-dark-mode.svg#gh-dark-mode-only)

# Installation and Getting Started

#### Install Versatile Data Kit SDK

```bash
pip install -U pip setuptools wheel
pip install quickstart-vdk
```
Note that Versatile Data Kit requires Python 3.7+.

See the [Installation page](https://github.com/vmware/versatile-data-kit/wiki/Installation#install-sdk) for more details.

#### Use

```bash
# see Help to see what you can do
vdk --help
```
Check out the [Getting Started page](https://github.com/vmware/versatile-data-kit/wiki/getting-started) to create and run your first Data Job.

# Documentation

Official documentation for Versatile Data Kit can be found [here](https://github.com/vmware/versatile-data-kit/wiki/Introduction).

# Contributing

If you are interested in contributing as a developer, visit [CONTRIBUTING.md](CONTRIBUTING.md).

# Contacts
Feedback is very welcome via the [GitHub site as issues](https://github.com/vmware/versatile-data-kit/issues) or [pull requests](https://github.com/vmware/versatile-data-kit/pulls)

* Join our dedicated Slack channel on the CNCF Slack workspace:
    * First [Join CNCF Slack workspace](https://communityinviter.com/apps/cloud-native/cncf)
    * Then search for #versatile-data-kit or [click here to join the channel](https://cloud-native.slack.com/archives/C033PSLKCPR)

- [Follow us on twitter](https://twitter.com/intent/follow?screen_name=VDKProject).
- Subscribe to the [Versatile Data Kit YouTube Channel](https://www.youtube.com/channel/UCasf2Q7X8nF7S4VEmcTHJ0Q).

- [Join our mailing list](mailto:join-versatiledatakit@groups.vmware.com?subject=Invite%20me%20to%20the%20VDK%20mailing%20list)

# How to use Versatile Data Kit?
- Video [Data Ingestion with Versatile Data Kit](https://youtu.be/JRV_5cxVQDU)
- Video [Data Transformation with Versatile Data Kit](https://youtu.be/2F6_REtupgA)
- Blog Post [A complete example using the Versatile Data Kit and Trino DB](https://towardsdatascience.com/from-raw-data-to-a-cleaned-database-a-deep-dive-into-versatile-data-kit-ab5fd992a02e)

For the full list of resources go to [Community and Resources](https://github.com/vmware/versatile-data-kit/wiki/Community-and-Resources)

# Code of Conduct
Everyone involved in working on the project's source code, or engaging in any issue trackers, Slack channels and mailing lists is expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
