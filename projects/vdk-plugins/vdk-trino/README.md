<a href="https://pypistats.org/packages/vdk-trino" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-trino.svg" alt="monthly download count for vdk-trino"></a>

This plugin allows vdk-core to interface with and execute queries against a Trino database. Additionally, it can collect lineage data, assuming a lineage logger has been provided through the vdk-core configuration.


# Usage

Run
```bash
pip install vdk-trino
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
They need to provide ILineageLogger implementation and hook this way:
```python
    @hookimpl
    def vdk_initialize(context: CoreContext) -> None:
        context.state.set(StoreKey[ILineageLogger]("trino-lineage-logger"), MyLogger())
```

### Ingestion

This plugin allows users to [ingest](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L90) data to a Trino database, which can be preferable to inserting data manually as it automatically handles serializing, packaging and sending of the data asynchronously with configurable batching and throughput. To do so, you must set the expected variables to connect to Trino, plus the following environment variable:
```sh
export VDK_INGEST_METHOD_DEFAULT=TRINO
```

Then, from inside the run function in a Python step, you can use the `send_object_for_ingestion` or `send_tabular_data_for_ingestion` methods to ingest your data.

### Multiple Trino Database Connections

#### Configuring Multiple Trino Databases

To effectively manage multiple Trino database connections within a data job, configure the default database in the `[vdk]` section of the `config.ini` file. This section should contain the primary connection details that the application will use by default.

For each additional Trino database, add a new section following the pattern `vdk_<name>`, where `<name>` is a unique identifier for each database connection. These additional sections must also include all necessary Trino connection details.

#### Example `config.ini` with Multiple Trino Databases

```ini
[vdk]
trino_user=user
trino_password=password
trino_host=localhost
trino_port=28080
trino_schema=default
trino_catalog=memory
trino_use_ssl=True

[vdk_trino_reports]
trino_user=reports_user
trino_password=reports_password
trino_host=reports_host
trino_port=28081
trino_schema=reports
trino_catalog=memory
trino_use_ssl=False
```

You can specify which database to use in your data job by referencing the specific section name.

```python
def run(job_input):

    # Querying the default Trino database
    default_query = "SELECT * FROM default_table"
    job_input.execute_query(sql=default_query, database="trino") # database option can be omitted

    # Querying the reports Trino database
    reports_query = "SELECT * FROM reports_table"
    job_input.execute_query(sql=reports_query, database="trino_reports") # database is mandatory; if omitted query will be executed against default db
```

#### Ingestion into Multiple Trino Databases

For data ingestion, you can also specify the target database to ensure the data is sent to the correct Trino instance.

```python
def run(job_input):

    # Ingest data into the default database
    payload_default = {"col1": "value1", "col2": "value2"}
    job_input.send_object_for_ingestion(
        payload=payload_default,
        destination_table="default_table",
        method="trino"
    )

    # Ingest data into the reports database
    payload_reports = {"col1": "value3", "col2": "value4"}
    job_input.send_object_for_ingestion(
        payload=payload_reports,
        destination_table="reports_table",
        method="trino_reports"
    )
```

# Configuration

Run vdk config-help - search for those prefixed with "TRINO_" to see what configuration options are available.

# Testing

Testing this plugin locally requires installing the dependencies listed in vdk-plugins/vdk-trino/requirements.txt

Run
```bash
pip install -r requirements.txt
```
