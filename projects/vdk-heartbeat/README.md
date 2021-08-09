# Versatile Data Kit Heartbeat tool

Heartbeat tool for verifying deployed SDK and Control Service are functional and working correctly.<br>
It  checks that a job can be created, deployed, run and deleted.

* Health monitoring - one can schedule this run every few minutes and get heartbeat of their installation
* Regression testing after change in Versatile Data Kit, as clients would be able to customize vdk, they should have a way to check for regressions.
* Installation/Upgrade of VDK Control Service acceptance test.

## What it does ?

It simulates Data Engineer workflow: 
* Creates a data job, downloads keytab
* Deploys the data job with pre-defined scripts to run on a scheduled basis (every minute)
* The Data Job executes basic transformations using most of Versatile Data Kit functionality (templates, properteis, etc.)
* Check the results of the job have been produced as expected
* Undeploys and deletes the data job 

## Prerequisites

See [heartbeat_config_example.ini](vdk-heartbeat/heartbeat_config_example.ini) and complete the TODOs inside

## Installation

```bash
# TODO: Change to public PYPI index
pip install -i https://test.pypi.org/simple/ vdk-heartbeat
```

## Running

You can run the test locally, part of your CICD or schedule it to run periodically. <br>

The test is passed or fail test. <br> If it fails it returns non-zero error code and prints the error.<br>

* Specify configuration in environment variables or in a file (use the file for things that can be in source control)
* Example:
```bash
export DATABASE_PASS=xxx
vdk-heartbeat -f heartbeat_config.ini
```
If you need to run concurrent tests use different job names
```
export JOB_NAME=...
```

## Notes
* The test currently does not clean fully after itself. It leaves the created tables behind.
  It cleans the data older than a day.

## Extensibility
To add new custom checks simply add them as new steps in the Heartbeat Data Job:
* The steps should be before the original steps of the test.
* If a check fails, fail the step (e.g. throw exception) - this will fail the whole test.
