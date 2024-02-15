# duckdb

<a href="https://pypistats.org/packages/vdk-duckdb" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-duckdb.svg" alt="monthly download count for vdk-duckdb"></a>

DuckDB plugin for the Versatile Data Kit (VDK), which enables users to connect to and interact with DuckDB databases.
The purpose is to simplify data extraction, transformation, and loading tasks when working with DuckDB as a data source or destination

## Usage

```
pip install vdk-duckdb
```

### Configuration

Run `vdk config-help` to browse all available configuration options for your VDK installation.


### Example

#### Query Execution

You specify you want to use duckdb in the job config file
config.ini
```
[vdk]
db_default_type = duckdb
```

Then you can use it
```
    def run(job_input: IJobInput):
        job_input.execute_query("select 'Hi Duck!'")
```

#### Ingestion

This plugin allows users to ingest data to a DuckDB database, which can be preferable to inserting data manually as it automatically handles serializing, packaging and sending of the data asynchronously with configurable batching and throughput.
To do so, you must set the expected variables to connect to Greenplum, plus the following environment variable:

export VDK_INGEST_METHOD_DEFAULT=DUCKDB

Then, from inside the run function in a Python step, you can use the `send_object_for_ingestion` or `send_tabular_data_for_ingestion` methods to ingest your data.

### Build and testing

```
pip install -r requirements.txt
pip install -e .
pytest
```

In VDK repo [../build-plugin.sh](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/build-plugin.sh) script can be used also.


#### Note about the CICD:

.plugin-ci.yaml is needed only for plugins part of [Versatile Data Kit Plugin repo](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins).

The CI/CD is separated in two stages, a build stage and a release stage.
The build stage is made up of a few jobs, all which inherit from the same
job configuration and only differ in the Python version they use (3.7, 3.8, 3.9 and 3.10).
They run according to rules, which are ordered in a way such that changes to a
plugin's directory trigger the plugin CI, but changes to a different plugin does not.
