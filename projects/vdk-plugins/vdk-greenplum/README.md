<a href="https://pypistats.org/packages/vdk-greenplum" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-greenplum.svg" alt="monthly download count for vdk-greenplum"></a>

This plugin allows vdk-core to interface with and execute queries against a Greenplum database.

# Usage

Run
```bash
pip install vdk-greenplum
```

After this, data jobs will have access to a Greenplum database connection, managed by Versatile Data Kit SDK.

If it is the only database plugin installed , vdk would automatically use it.
Otherwise, users need to set VDK_DB_DEFAULT_TYPE=GREENPLUM as an environment variable or set 'db_default_type' option in the data job config file (config.ini).

For example

```python
    def run(job_input: IJobInput):
        job_input.execute_query("select 'Hi Greenplum!'")
```

## Ingestion

This plugin allows users to [ingest](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L90) data to a Greenplum database,
which can be preferable to inserting data manually as it automatically handles serializing, packaging and sending of the data asynchronously with configurable batching and throughput.
To do so, you must set the expected variables to connect to Greenplum, plus the following environment variable:
```sh
export VDK_INGEST_METHOD_DEFAULT=GREENPLUM
```

Then, from inside the run function in a Python step, you can use the `send_object_for_ingestion` or `send_tabular_data_for_ingestion` methods to ingest your data.

# Configuration

Run vdk config-help - search for those prefixed with "GREENPLUM_" to see what configuration options are available.

# Testing

Testing this plugin locally requires installing the dependencies listed in vdk-plugins/vdk-greenplum/requirements.txt

Run
```bash
pip install -r requirements.txt
```
