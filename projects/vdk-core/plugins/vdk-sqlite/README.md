This plugin allows vdk-core to interface with and execute queries against a Sqlite database.

# Usage

Run
```bash
pip install vdk-sqlite
```

After this data jobs will have access to sqlite database connection managed by Versatile Data Kit SDK.

If it is the only database plugin installed , vdk would automatically use it.
Otherwise, users need to set VDK_DB_DEFAULT_TYPE=SQLITE as an environment variable or set 'db_default_type' option in the data job config file (config.ini).

For example

```python
    def run(job_input: IJobInput):
        job_input.execute_query("select 'Hi SqLite!'")
```

## Configuration

When set as environment variables those options are prefixed with "VDK_"

| Name | Description | (most likely) value |
|---|---|---|
| DB_DEFAULT_TYPE | The type of database used in data job queries by default | SQLITE |
| SQLITE_DIRECTORY | Where on local file system the database files will be stored  | Temp directory |
|  |  |  |
