This plugin allows vdk-core to interface with and execute queries against an Impala database.

# Usage

Run
```bash
pip install vdk-impala
```

After this, data jobs will have access to a Impala database connection, managed by Versatile Data Kit SDK.

If it is the only database plugin installed , vdk would automatically use it.
Otherwise, users need to set `VDK_DB_DEFAULT_TYPE=IMPALA` as an environment variable or set 'db_default_type' option in the data job config file (config.ini).

For example

```python
    def run(job_input: IJobInput):
        job_input.execute_query("select 'Hi Impala!'")
```

<!-- ## Ingestion - not yet implemented so this part is commented out

This plugin allows users to [ingest](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L90) data to an Impala database,
which can be preferable to inserting data manually as it automatically handles serializing, packaging and sending of the data asynchronously with configurable batching and throughput.
To do so, you must set the expected variables to connect to Impala, plus the following environment variable:
```sh
export VDK_INGEST_METHOD_DEFAULT=IMPALA
```

Then, from inside the run function in a Python step, you can use the `send_object_for_ingestion` or `send_tabular_data_for_ingestion` methods to ingest your data.
-->

# Configuration

Run vdk config-help - search for those prefixed with "IMPALA_" to see what configuration options are available.

# Disclaimer

This plugin is tested against a specific impala version. The version comes from the docker-compose.yaml container's impala version. For more information on the imapala version tested against please google the docker image.

# Testing

Testing this plugin locally requires installing the dependencies listed in vdk-plugins/vdk-impala/requirements.txt

Run
```bash
pip install -r requirements.txt
```
