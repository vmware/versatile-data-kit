This plugin allows vdk-core to interface with and execute queries against an Impala database.
Additionally, it can collect lineage data, assuming a lineage logger has been provided through the vdk-core configuration.

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

### Lineage

The package can gather lineage data for all successful Impala SQL queries that have actually read or written data.
Other plugins can read and optionally send the lineage data to separate system.
They need to provide ILineageLogger implementation and hook this way:
```python
    @hookimpl
    def vdk_initialize(context: CoreContext) -> None:
        context.state.set(StoreKey[ILineageLogger]("impala-lineage-logger"), MyLogger())
```

Lineage is calculated based on the executed query profile. It is retrieved via the cursor by executing additional RPC
request against the same Impala node that has coordinated the query right after the original query has successfully
finished. See https://impala.apache.org/docs/build/html/topics/impala_logging.html for more information how profiles are
stored and here https://impala.apache.org/docs/build/impala-3.1.pdf for more information about the profiles themselves.

If enabled, query plan is retrieved for every successfully executed query against Impala excluding keepalive queries
like "Select 1".

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
