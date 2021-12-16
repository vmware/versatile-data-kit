This plugin allows vdk-core to interface with and execute queries against a Trino database. Additionally, it can collect lineage data, assuming a lineage logger has been provided through the vdk-core configuration.


# Usage

Run
```bash
pip install vdk-tino
```

After this data jobs will have access to Trino database connection managed by Versatile Data Kit SDK.

If it is the only database plugin installed , vdk would automatically use it.
Otherwise, users need to set VDK_DB_DEFAULT_TYPE=TRINO as an environment variable or set 'db_default_type' option in the data job config file (config.ini).

For example

```python
    def run(job_input: IJobInput):
        job_input.execute_query("select 'Hi Trino!'")
```

### Templates

vdk-trino comes with pre-defined templates for SQL transformations

* SCD1 - [Slowly Changing Dimension type 1](https://en.wikipedia.org/wiki/Slowly_changing_dimension#Type_1:_overwrite):
  - [See usage documentation here](src/vdk/plugin/trino/templates/load/dimension/scd1/README.md)
* SCD2 - [Slowly Changing Dimension Type 2](https://en.wikipedia.org/wiki/Slowly_changing_dimension#Type_2:_add_new_row):
  - [See usage documentation here](src/vdk/plugin/trino/templates/load/dimension/scd2/README.md)

### Lineage

The package gathers lineage data for all Trino SQL queries executed in a data job

Other plugins can read that lineage data log it.
They need to provide LineageLogger implementation and hook this way:
```python
    @hookimpl
    def vdk_initialize(context: CoreContext) -> None:
        context.state.set(StoreKey[LineageLogger]("trino-lineage-logger"), MyLogger())
```

### Ingestion

This plugin allows users to [ingest](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L90) data to a Trino database, which can be preferable to inserting data manually as it automatically handles serializing, packaging and sending of the data asynchronously with configurable batching and throughput. To do so, you must set the expected variables to connect to Trino, plus the following environment variable:
```sh
export VDK_INGEST_METHOD_DEFAULT=TRINO
```

Then, from inside the run function in a Python step, you can use the `send_object_for_ingestion` or `send_tabular_data_for_ingestion` methods to ingest your data.
# Configuration

Run vdk config-help - search for those prefixed with "TRINO_" to see what configuration options are available.

# Testing

Testing this plugin locally requires installing the dependencies listed in vdk-plugins/vdk-trino/requirements.txt

Run
```bash
pip install -r requirements.txt
```
