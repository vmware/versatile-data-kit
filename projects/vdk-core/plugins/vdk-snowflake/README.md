# Versatile Data Kit Plugin for Snowflake Support

This plugin provides functionality, used by the Versatile Data Kit
to interact with a Snowflake instance. Users of the plugin can connect to
Snowflake, and execute queries against it.

### Instalation

To install the plugin, open a terminal and type
```bash
pip install --upgrade vdk-snowflake
```

### Usage

In order to use the plugin, once it has been installed, there are a few environment variables that need to be set.

The following environment variables are required:

```bash
\\ Set default database plugin to be used
VDK_DB_DEFAULT_TYPE=SNOWFLAKE

\\ Set the username that is to be used.
VDK_SNOWFLAKE_USER=<some_username>

\\ Set the password that is to be used.
VDK_SNOWFLAKE_PASSWORD=<user_password>

\\ Set the account name that is to be used.
\\ NOTE: Do NOT include the '.snoflakecomputing.com' part of the account name.
VDK_SNOWFLAKE_ACCOUNT=<account_name_provided_by_snowflake>
```

The following environment variables are optional, and can be overwritten from within the data job.

```bash
\\ The default warehouse to be used.
VDK_SNOWFLAKE_WAREHOUSE=<default_warehouse>

\\ The default database to be used.
VDK_SNOWFLAKE_DATABASE=<default_database>

\\ The default database schema to be used.
VDK_SNOWFLAKE_SCHEMA=<default_schema>
```

After configuring the environment variables, to use the plugin, create a data job, and add the queries you want to execute in `.sql` files. When the job executed, Versatile Data Kit will execute the queries in the order specified in the [User Guide](https://github.com/vmware/versatile-data-kit/wiki/User-Guide#data-job-steps).
