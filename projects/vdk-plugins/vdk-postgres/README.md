<a href="https://pypistats.org/packages/vdk-postgres" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-postgres.svg" alt="monthly download count for vdk-postgres"></a>

This plugin allows vdk-core to interface with and execute queries against a PostgreSQL database.

# Usage

Run
```bash
pip install vdk-postgres
```

After this, data jobs will have access to a Postgres database connection, managed by Versatile Data Kit SDK.

If you want to use single postgres database instance.
If it is the only database plugin installed , vdk would automatically use it.
Otherwise, users need to set VDK_DB_DEFAULT_TYPE=POSTGRES as an environment variable or set 'db_default_type' option in the data job config file (config.ini).

Add the required configuration values using the config file, environment variables, or VDK secrets.
The supported configuration variables include:
```text
POSTGRES_DSN - libpq connection string. Check https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
POSTGRES_DBNAME - database name
POSTGRES_USER - user name
POSTGRES_PASSWORD - user password
POSTGRES_HOST - the host we need to connect to, defaulting to UNIX socket, https://www.psycopg.org/docs/module.html"
POSTGRES_PORT - The port to connect to, defaulting to 5432
```
Set a default database in config.ini like this:
```ini
[vdk]
postgres_dbname=postgres
postgres_user=postgres
postgres_password=postgres
postgres_host=localhost
postgres_port=5433

```
Note: Default database configurations must be in the [vdk] section.

You can connect to the default database through 'job_input'. For instance

```python
    def run(job_input: IJobInput):
        job_input.execute_query("select 'Hi Postgres!'")
```

### Postgres Multiple Databases

To manage multiple Postgres database connections within a data job,
always configure the default database in the `[vdk]` section of the `config.ini` file.
This section should contain the primary connection details that the application will use by default.
The default Postgres connection is saved as `postgres` and should always be called with that name.
Subsections should not be created with that name. Subsection name `vdk_postgres` is prohibited.


For each additional Postgres database,
add a new section following the pattern `vdk_<name>`, where `<name>` is a unique identifier for each database connection.
These additional sections must also include all necessary Postgres connection details.

Note: When using in code the `<name>` should be lowercased.
For example, if you have `vdk_DEV`, in the data job you should refer to the database using the `dev` string.


Here's an example config.ini with an additional database:

```ini
[vdk]
postgres_dbname=postgres
postgres_user=postgres
postgres_password=postgres
postgres_host=localhost
postgres_port=5432

[vdk_postgres_second]
postgres_dbname=postgres_second
postgres_user=reports_user
postgres_password=postgres
postgres_host=localhost
postgres_port=5433

```

To connect to databases, use the 'job_input'.
Here's an example that demonstrates creating tables in default and secondary databases:

```python
    def run(job_input: IJobInput):
            job_input.execute_query(
        sql="CREATE TABLE default_table "
        "(some_data varchar, more_data varchar, "
        "int_data bigint, float_data real, bool_data boolean)",
        database="postgres", # executed against the default; database option can be omitted
    )

    job_input.execute_query(
        sql="CREATE TABLE secondary_table "
        "(some_data varchar, more_data varchar, "
        "int_data bigint, float_data real, bool_data boolean)",
        database="postgres_second", # executed against the secondary; database option is mandatory if omitted it will be executed against the default
    )
```

VDK also supports data ingestion.
Here's an example of sending data for ingestion into the default and secondary databases:
```python
        def run(job_input: IJobInput):
            .....
        job_input.send_object_for_ingestion(
            payload=payload,
            destination_table="default_table",
            method="postgres",
            target="postgres",
        )
        job_input.send_object_for_ingestion(
            payload=payload,
            destination_table="secondary_table",
            method="postgres_second",
            target="postgres_second",
        )
```


#### Secrets with Multiple Postgres Databases

If you have a config like above, for the default `vdk` section, secrets overrides work like usual.
For example, to override `postgres_user=your_user`, you should create a secret `postgres_user` with value `your_user`.

If you want to override a config property for a subsection, you have to prefix the secret
with the subsection name without `vdk`.
For example, to override `postgres_user=reports_user` for vdk_postgres_second,
create a secret `postgres_second_postgres_user` with value `reports_user`.

#### Environmental variables with Multiple Postgres Databases

Environment variables work pretty much the same way as secrets. For the above config:
```shell
export VDK_POSTGRES_USER=user # overrides postgres_user=user in section [vdk] (default postgres)
export VDK_POSTGRES_SECOND_POSTGRES_USER=reports_user # overrides postgres_user=reports_user in section [vdk_postgres_second]
```

Note: Environment variable overrides take precedence over secrets.
For example, if you have a secret `postgres_second_postgres_user=reports_user`
and an env variable `VDK_POSTGRES_SECOND_POSTGRES_USER=another_reports_user` the value of
postgres_user for section `vdk_postgres_second` will be `another_reports_user`.

# Configuration

You can also run vdk config-help - search for those prefixed with "POSTGRES_" to see what configuration options are available.

# Testing

Testing this plugin locally requires installing the dependencies listed in vdk-plugins/vdk-postgres/requirements.txt

Run
```bash
pip install -r requirements.txt
```
