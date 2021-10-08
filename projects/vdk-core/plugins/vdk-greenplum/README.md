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

# Configuration

Run vdk config-help - search for those prefixed with "GREENPLUM_" to see what configuration options are available.

# Testing

Testing this plugin locally requires installing the dependencies listed in plugins/vdk-greenplum/requirements.txt

Run
```bash
pip install -r requirements.txt
```
