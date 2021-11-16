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
* Different data jobs and run tests can be run depending on the configuration.
  * This way it can be run in different modes. See [config.py](src/taurus/vdk/heartbeat/config.py)  and the DATAJOB_DIRECTORY_* and JOB_RUN_TEST_* configuration options.
* Undeploys and deletes the data job.

## Prerequisites

See [heartbeat_config_example.ini](vdk-heartbeat/heartbeat_config_example.ini) and complete the TODOs inside

## Installation

```bash
# TODO: Change to public PYPI index
pip install -i https://test.pypi.org/simple/ vdk-heartbeat
```

## Configuration

 See [config.py](src/taurus/vdk/heartbeat/config.py) for details on what can be configured.

## Running

You can run the test locally, part of your CICD or schedule it to run periodically. <br>

The test is passed or fail test. <br> If it fails it returns non-zero error code and prints the error.<br>
It also produces a tests.xml file in junit xml format.

* Specify configuration in environment variables or in a file (use the file for things that can be in source control)
* Example:
```bash
export DATABASE_PASS=xxx
vdk-heartbeat -f heartbeat_config.ini
```

## Extensibility

Users can replace the data job being deployed and executed and the run test which is used to verify the job run/execution.

See [config.py](src/taurus/vdk/heartbeat/config.py) DATAJOB_DIRECTORY_* and JOB_RUN_TEST_* configuration options.


## Build, test, and release

See or run `cicd/build.sh` to build and test the project locally.

### Release

Releases are made to PyPI. <br>
Versioning follows https://semver.org.

* A release step in Gitlab CI is automatically triggered after merging changes if build/tests are successful.
* Update major or minor version when necessary only.

## Tests
### Database ingestion
The testing job ingests data into a database and reads it from that database to verify the results.
#### Configuration
##### Target
Target identifies where the data should be ingested into.

The value for this parameter depends on the ingest method chosen.
* For "http" method, it would require an HTTP URL.
    Example: http://example.com/<some>/<api>/<endpoint>
* For "file" method, it would require a file name or path.
```
export VDK_HEARTBEAT_INGEST_TARGET="datasource"
```
##### Method
Indicates the ingestion method to be used. Example:
* method="file" -> ingest to file
* method="http" -> ingest using HTTP POST requests
* method="kafka" -> ingest to kafka endpoint
```
export VDK_HEARTBEAT_INGEST_METHOD="http"
```
##### Destination table
The name of the table, where the data should be ingested into.
This parameter does not need to be passed, in case the table is
included in the payload itself.
```
export VDK_HEARTBEAT_INGEST_DESTINATION_TABLE="destination_table"
```
##### Database type
```
export DB_DEFAULT_TYPE="trino"
```
##### Database name
```
export DATABASE_TEST_DB="memory.default"
```
#### Scenarios
##### Trino ingestion
VDK_HEARTBEAT_INGEST_METHOD is set to "TRINO" and DB_DEFAULT_TYPE is set to "TRINO"
and the connection settings for both is the same (same Trino database instance).
```
export VDK_HEARTBEAT_INGEST_TARGET="trino-http-datasource"
export VDK_HEARTBEAT_INGEST_METHOD="TRINO"
export VDK_HEARTBEAT_INGEST_DESTINATION_TABLE="sample_destination_table"
export DB_DEFAULT_TYPE="trino"
export DATABASE_TEST_DB="memory.default"
```
##### Trino HTTP ingestion
VDK_HEARTBEAT_INGEST_METHOD is set to "HTTP" and DB_DEFAULT_TYPE is set to "TRINO"
and connection settings are set to same Trino instance.
```
export VDK_HEARTBEAT_INGEST_TARGET="trino-http-datasource"
export VDK_HEARTBEAT_INGEST_METHOD="http"
export VDK_HEARTBEAT_INGEST_DESTINATION_TABLE="sample_destination_table"
export DB_DEFAULT_TYPE="trino"
export DATABASE_TEST_DB="memory.default"
```
