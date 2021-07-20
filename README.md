# Overview

Versatile Data Kit is a data engineering framework that enables Data Engineers develop, troubleshoot, deploy, run, and manage data processing workloads (called "Data Job").
"Data Job" enables Data Engineers to implement automated pull ingestion (E in ELT) and batch data transformation (T in ELT) into a Data Warehouse

# About Versatile Data Kit

The abstraction of the common data engineering problems, provided by Versatile Data Kit, accelerates development of data applications and helps to manage data applications, making sure they are packaged, versioned and deployed correctly. Tracking both code and data modifications and relations between them enables engineers to troubleshoot more quickly and provides easy revert to a stable version

Versatile Data Kit consists of:

* Control Service which enables creating, deploying, managing and executing Data Jobs in Kubernetes runtime environment. It has multitenancy support, SSO, Access Control and auditing capabilities
* Command line tool for data engineers to use locally to create by sample, deploy, list and manage Data Jobs in the Cloud
* A development Kit to develop, test and run Data Jobs on your machine. It comes with common functionality for data ingestion and processing like: 
    * sending data for ingestion from different sources to different destinations
    * integrating raw table data into a dimensional model in Data Warehouse 
    * Extremely extensible and adaptable to your organizations use-cases
    * and many others


# Installation and Getting Started

#### Install Versatile Data Kit Control Service

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install bitnami/pipelines-control-service
```

#### Install Versatile Data Kit SDK

```bash
pip install vdk
```

#### Use

```bash
# see Help to see what you can do
vdk --help 
# create a new job and start playing around.
vdk create -u <URI-YOU-GOT-FROM-helm-install-OUTPUT>
```

# Documentation

# Contributing 

If you are interested in contributing as a developer, visit [CONTRIBUTING.md](CONTRIBUTING.md).

# Contacts 
We can reach out to us through slack, mail. 

# Code of Conduct
Everyone interacting in the project's source code, issue trackers, slack channels, and mailing lists is expected to follow the [Code of Conduct](CODE-OF-CONDUCT.md).

