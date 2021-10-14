![Versatile Data Kit](./support/images/versatile-data-kit.svg)

<p align="center">
    <a href="https://github.com/badges/shields/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/vmware/versatile-data-kit" /></a>
    <a href="https://github.com/badges/shields/graphs/contributors" alt="Last Activity">
        <img src="https://img.shields.io/github/last-commit/vmware/versatile-data-kit" alt="Last Activity"></a>
    <a href="https://github.com/vmware/versatile-data-kit/blob/main/LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/vmware/versatile-data-kit" alt="license"></a>
    <a href="https://github.com/pre-commit/pre-commit">
        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="pre-commit"></a>
    <a href="https://github.com/vmware/versatile-data-kit">
        <img src="https://gitlab.com/vmware-analytics/versatile-data-kit/badges/main/pipeline.svg" alt="build status"></a>
    <!-- TODO: code coverage -->
</p>

# Overview

Versatile Data Kit is a data engineering framework that enables Data Engineers to develop, troubleshoot, deploy, run, and manage data processing workloads (referred to as "Data Jobs").
A "Data Job" enables Data Engineers to implement automated pull ingestion (E in ELT) and batch data transformation (T in ELT) into a database.

# About Versatile Data Kit

Versatile Data Kit provides an abstraction layer that helps solve common data engineering problems.
It can be called by the workflow engine with the goal of making data engineers more efficient
(for example, it ensures data applications are packaged, versioned and deployed correctly,
while dealing with credentials, retries, reconnects, etc.).
Everything exposed by Versatile Data Kit provides built-in monitoring, troubleshooting,
and smart notification capabilities. For example, tracking both code and data modifications and the relations between them
enables engineers to troubleshoot more quickly and provides an easy revert to a stable version.

Versatile Data Kit consists of:

* Control Service which enables creating, deploying, managing and executing Data Jobs in a Kubernetes runtime environment.
  It offers multitenancy support, SSO, Access Control and auditing capabilities. It exposes CLI.
* A development Kit to develop, test and run Data Jobs on your machine. It comes with common functionality for data ingestion and processing.


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
You can join our public Slack workspace by clicking [here](https://join.slack.com/t/versatiledata-rgg2437/shared_invite/zt-tvnl62c3-qP0EUYJZJxb6Ws_eQWyDtQ) or request to join our mailing list by emailing [here](mailto:join-versatiledatakit@groups.vmware.com?subject=Invite%20me%20to%20the%20VDK%20mailing%20list).

# Code of Conduct
Everyone involved in working on the project's source code, or engaging in any issue trackers, Slack channels and mailing lists is expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
