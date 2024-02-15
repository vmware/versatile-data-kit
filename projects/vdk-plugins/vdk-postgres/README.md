<a href="https://pypistats.org/packages/vdk-postgres" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-postgres.svg" alt="monthly download count for vdk-postgres"></a>

This plugin allows vdk-core to interface with and execute queries against a PostgreSQL database.

# Usage

Run
```bash
pip install vdk-postgres
```

After this, data jobs will have access to a Postgres database connection, managed by Versatile Data Kit SDK.

If it is the only database plugin installed , vdk would automatically use it.
Otherwise, users need to set VDK_DB_DEFAULT_TYPE=POSTGRES as an environment variable or set 'db_default_type' option in the data job config file (config.ini).

For example

```python
    def run(job_input: IJobInput):
        job_input.execute_query("select 'Hi Postgres!'")
```

# Configuration

Run vdk config-help - search for those prefixed with "POSTGRES_" to see what configuration options are available.

# Testing

Testing this plugin locally requires installing the dependencies listed in vdk-plugins/vdk-postgres/requirements.txt

Run
```bash
pip install -r requirements.txt
```
