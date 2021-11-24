This plugin allows vdk-core to interface with, execute queries against, and ingest data to a SQLite database.

# Usage

Run
```bash
pip install vdk-sqlite
```

After this Data Jobs will have access to a SQLite database connection managed by Versatile Data Kit.

If it is the only database plugin installed , VDK would automatically use it.
Otherwise, users need to set VDK_DB_DEFAULT_TYPE=SQLITE as an environment variable or set 'db_default_type' option in the data job config file (config.ini).

For example:

```python
    def run(job_input: IJobInput):
        job_input.execute_query("select 'Hi SqLite!'")
```

Data ingestion requires setting either the VDK_SQLITE_FILE,
or the VDK_INGEST_TARGET_DEFAULT to the path to the SQLite database file,
or setting the 'target' parameter for the `send_object_for_ingestion` method, and can be done like so:
```python
    def run(job_input: IJobInput):
        payload = ...  # generate your payload

        job_input.send_object_for_ingestion(
            payload=payload,
            destination_table="name_of_destination_table"
        )
```

## Configuration

When set as environment variables those options are prefixed with "VDK_"

| Name | Description | (most likely) value |
|---|---|---|
| DB_DEFAULT_TYPE | The type of database used in data job queries by default | SQLITE |
| SQLITE_FILE | Where on local file system the database file is stored  | SQLITE file in temp directory |
|  |  |  |
