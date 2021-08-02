# Versatile Data Kit SDK Core

To build or contribute, see [CONTRIBUTING.md](./CONTRIBUTING.md).

Versatile Data Kit enables data engineers, data scientists and data analysts to develop, deploy, run, and manage data processing workloads (called "Data Job").
A "Data Job" enables Data Engineers to implement automated pull ingestion (E in ELT) and batch data transformation into a Data Warehouse (T in ELT).

## Build

Make sure you have python3 installed. It's strongly recommended to use a virtual environment, and also to use a python installer like pyenv or conda. We recommend pyenv.

CICD is managed through gitlab-ci.yml. You can see how to build, run tests, deploy there best.
All related CICD scripts are in /cicd/ folder.

## Installation

All Versatile Data Kit SDK Core releases can be found in PyPI.

Install Versatile Data Kit SDK Core with:
```bash
pip install vdk-core
```
This will install console application called `vdk`

Then run help to see what it can do:
```bash
vdk --help
```

## Plugins

Plugins are a powerful way of extending or adapting Versatile Data Kit for all kinds of use-cases.
For more information see [Plugins doc](./README_PLUGINS.md).
