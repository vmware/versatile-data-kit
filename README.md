# Overview

Versatile Data Kit is a data engineering framework that enables Data Engineers to develop, troubleshoot, deploy, run, and manage data processing workloads (called "Data Job").
"Data Job" enables Data Engineers to implement automated pull ingestion (E in ELT) and batch data transformation (T in ELT) into a Data Warehouse

# About Versatile Data Kit

Versatile Data Kit provides an abstraction layer that helps solve common data engineering problems.
It can be called by the workflow engine with the goal to make data engineers more efficient
(for example, it make sure data applications are packaged, versioned and deployed correctly,
dealing with credentials, retries, reconnects, etc.).
Everything exposed by Versatile Data Kit includes built-in monitoring, troubleshooting,
and smart notifications capabilities.
(for example, tracking both code and data modifications and relations between them
enables engineers to troubleshoot more quickly and provides an easy revert to a stable version)

Versatile Data Kit consists of:

* Control Service which enables creating, deploying, managing and executing Data Jobs in Kubernetes runtime environment.
  It has multitenancy support, SSO, Access Control and auditing capabilities. It exposes CLI.
* A development Kit to develop, test and run Data Jobs on your machine. It comes with common functionality for data ingestion and processing


# Installation and Getting Started

#### Install Versatile Data Kit SDK

```bash
pip install quickstart-vdk
```

#### Use

```bash
# see Help to see what you can do
vdk --help
# create a new job and start playing around.
vdk run first-job-directory
```

For more see [Getting Started page](https://github.com/vmware/versatile-data-kit/wiki/getting-started)

# Documentation

Official documentation for Versatile Data Kit can be found [here](https://github.com/vmware/versatile-data-kit/wiki/Introduction).

# Contributing

If you are interested in contributing as a developer, visit [CONTRIBUTING.md](CONTRIBUTING.md).

# Contacts
You can reach out to us through mail, or join our public Slack workspace [here](https://versatiledata-rgg2437.slack.com/).
<!--- TODO: Set up a slackin web app to make joining easier --->

# Code of Conduct
Everyone interacting in the project's source code, issue trackers, slack channels, and mailing lists is expected to follow the [Code of Conduct](CODE-OF-CONDUCT.md).
