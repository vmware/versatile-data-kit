# oracle

<a href="https://pypistats.org/packages/vdk-oracle" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-oracle.svg" alt="monthly download count for vdk-oracle"></a>

Support for VDK Managed Oracle connection

TODO: what the project is about, what is its purpose


## Usage

```
pip install vdk-oracle
```

### Configuration

(`vdk config-help` is useful command to browse all config options of your installation of vdk)

| Name                     | Description                                                                                                                                                                                                                           | (example)  Value    |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------|
| oracle_user              | Username used when connecting to Oracle database                                                                                                                                                                                      | my_user             |
| oracle_password          | Password used when connecting to Oracle database                                                                                                                                                                                      | super_secret_shhhh  |
| oracle_use_secrets       | Set to True to use secrets to connect to Oracle                                                                                                                                                                                       | True                |
| oracle_connection_string | The Oracle connection string                                                                                                                                                                                                          | localhost:1521/free |
| oracle_host              | The host of the Oracle database. Note: This gets overridden if oracle_connection_string is set.                                                                                                                                       | localhost           |
| oracle_port              | The port of the Oracle database. Note: This gets overridden if oracle_connection_string is set.                                                                                                                                       | 1521                |
| oracle_sid               | The SID of the Oracle database. Note: This gets overridden if oracle_connection_string is set.                                                                                                                                        | free                |
| oracle_service_name      | The Service name of the Oracle database. Note: This gets overridden if oracle_connection_string is set.                                                                                                                               | free                |
| oracle_thick_mode        | Python-oracledb is said to be in Thick mode when Oracle Client libraries are used. True by default. Set to False to disable Oracle Thick mode. More info: https://python-oracledb.readthedocs.io/en/latest/user_guide/appendix_b.html | True                |
| oracle_ingest_batch_size | vdk-oracle splits ingestion payloads into batches. Change this config to control the batch size. Default is set to 100.                                                                                                               | 100                 |

### Example

#### CLI Queries

```sh
export VDK_ORACLE_USER=my_username
export VDK_ORACLE_PASSWORD=my_password
export VDK_ORACLE_CONNECTION_STRING=localhost:1521/free
vdk oracle-query -q "SELECT * FROM TEST_TABLE"
```

**Note:** Running CLI queries does not support secrets

#### Ingestion

```python
import datetime
from decimal import Decimal

def run(job_input):

    # Ingest object
    payload_with_types = {
        "id": 5,
        "str_data": "string",
        "int_data": 12,
        "float_data": 1.2,
        "bool_data": True,
        "timestamp_data": datetime.datetime.fromtimestamp(1700554373),
        "decimal_data": Decimal(0.1),
    }

    job_input.send_object_for_ingestion(
        payload=payload_with_types, destination_table="test_table"
    )

    # Ingest tabular data
    col_names = [
        "id",
        "str_data",
        "int_data",
        "float_data",
        "bool_data",
        "timestamp_data",
        "decimal_data",
    ]
    row_data = [
        [
            0,
            "string",
            12,
            1.2,
            True,
            datetime.datetime.fromtimestamp(1700554373),
            Decimal(1.1),
        ],
        [
            1,
            "string",
            12,
            1.2,
            True,
            datetime.datetime.fromtimestamp(1700554373),
            Decimal(1.1),
        ],
        [
            2,
            "string",
            12,
            1.2,
            True,
            datetime.datetime.fromtimestamp(1700554373),
            Decimal(1.1),
        ],
    ]
    job_input.send_tabular_data_for_ingestion(
        rows=row_data, column_names=col_names, destination_table="test_table"
    )
```

#### Ingestion with type inference

Ingestion works with an already created table even if you pass strings in the
payload. `vdk-oracle` infers the correct type based on the existing table.

```sql
create table test_table (
                            id number,
                            str_data varchar2(255),
                            int_data number,
                            float_data float,
                            bool_data number(1),
                            timestamp_data timestamp,
                            decimal_data decimal(14,8),
                            primary key(id))
```

```python
def run(job_input):
    payload = {
        "id": "5",
        "str_data": "string",
        "int_data": "12",
        "float_data": "1.2",
        "bool_data": "False",
        "timestamp_data": "2023-11-21T08:12:53",
        "decimal_data": "0.1",
    }

    job_input.send_object_for_ingestion(payload=payload, destination_table="test_table")
```

#### Case Sensitivity

**vdk-oracle supports only lower-case and upper-case payload keys.** Oracle is case-insensitive by default. This is a
challenge when ingesting payloads and doing type and schema inference, so we've opted for the simplest solution to
avoid confusion on the user side.

**Valid Ingestion**

```python
def run(job_input):
    payload = {
        "id": "5",
        "str_data": "string",
        "int_data": "12",
        "float_data": "1.2",
        "bool_data": "False",
        "timestamp_data": "2023-11-21T08:12:53",
        "decimal_data": "0.1",
    }

    job_input.send_object_for_ingestion(payload=payload, destination_table="test_table")
```

```python
def run(job_input):
    payload = {
        "ID": "5",
        "STR_DATA": "string",
        "INT_DATA": "12",
        "FLOAT_DATA": "1.2",
        "BOOL_DATA": "False",
        "TIMESTAMP_DATA": "2023-11-21T08:12:53",
        "DECIMAL_DATA": "0.1",
    }

    job_input.send_object_for_ingestion(payload=payload, destination_table="TEST_TABLE")
```

**Invalid ingestion**

Will infer the schema, but won't insert correctly.

```python
def run(job_input):
    payload = {
        "Id": "5",
        "Str_Data": "string",
        "Int_Data": "12",
        "Float_Data": "1.2",
        "Bool_Data": "False",
        "Timestamp_Data": "2023-11-21T08:12:53",
        "Decimal_Data": "0.1",
    }
    job_input.send_object_for_ingestion(payload=payload, destination_table="test_table")
```

### Multiple Oracle Database Connections

#### Configuring Multiple Oracle Databases

To manage multiple Oracle database connections within a data job,
always configure the default database in the `[vdk]` section of the `config.ini` file.
This section should contain the primary connection details that the application will use by default.
The default Oracle connection is saved as `oracle` and should always be called with that name.
Subsections should not be created with that name. Subsection name `vdk_oracle` is prohibited.

For each additional Oracle database,
add a new section following the pattern `vdk_<name>`, where `<name>` is a unique identifier for each database connection.
These additional sections must also include all necessary Oracle connection details.

Note: When using in code the `<name>` should be lowercased.
For example, if you have `vdk_DEV`, in the data job you should refer to the database using the `dev` string.

#### Example `config.ini` with Multiple Oracle Database Connections

```ini
[vdk]
oracle_user=user
oracle_password=password
oracle_host=localhost
oracle_port=1521
oracle_sid=FREE
oracle_connection_string =localhost:1521/FREE
oracle_thick_mode=True

[vdk_oracle_reports]
oracle_user=reports_user
oracle_password=reports_password
oracle_host=localhost
oracle_port=1523
oracle_sid=FREE
oracle_connection_string =localhost:1523/FREE
oracle_thick_mode=False

```

You can specify which database to use in your data job by referencing the specific section name.

```python
def run(job_input):

    # Querying the default Oracle database
    default_query = "SELECT * FROM default_table"
    job_input.execute_query(sql=default_query, database="oracle") # database option can be omitted

    # Querying the reports Oracle database
    reports_query = "SELECT * FROM reports_table"
    job_input.execute_query(sql=reports_query, database="oracle_reports") # database is mandatory; if omitted query will be executed against default db
```

#### Ingestion into Multiple Oracle Databases

For data ingestion, you can also specify the target database to ensure the data is sent to the correct Oracle instance.

```python
def run(job_input):

    # Ingest data into the default database
    payload_default = {"col1": "value1", "col2": "value2"}
    job_input.send_object_for_ingestion(
        payload=payload_default,
        destination_table="default_table",
        method="oracle",
        target="oracle"
    )

    # Ingest data into the reports database
    payload_reports = {"col1": "value3", "col2": "value4"}
    job_input.send_object_for_ingestion(
        payload=payload_reports,
        destination_table="reports_table",
        method="oracle_reports",
        target="oracle_reports"
    )
```

#### Secrets with Multiple Oracle Databases

If you have a config like above, for the default `vdk` section, secrets overrides work like usual.
For example, to override `oracle_user=your_user`, you should create a secret `oracle_user` with value `your_user`.

If you want to override a config property for a subsection, you have to prefix the secret
with the subsection name without `vdk`.
For example, to override `oracle_user=reports_user` for vdk_oracle_reports,
create a secret `oracle_reports_oracle_user` with value `reports_user`.

#### Environmental variables with Multiple Oracle Databases

Environment variables work pretty much the same way as secrets. For the above config:
```shell
export VDK_ORACLE_USER=user # overrides oracle_user=user in section [vdk] (default oracle)
export VDK_ORACLE_REPORTS_ORACLE_USER=reports_user # overrides oracle_user=reports_user in section [vdk_reports_user]
```

Note: Environment variable overrides take precedence over secrets.
For example, if you have a secret `oracle_reports_oracle_user=reports_user`
and an env variable `VDK_ORACLE_REPORTS_ORACLE_USER=another_reports_user` the value of
oracle_user for section `vdk_oracle_reports` will be `another_reports_user`.



### Build and testing

```
pip install -r requirements.txt
pip install -e .
pytest
```

In VDK repo [../build-plugin.sh](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/build-plugin.sh) script can be used also.


#### Note about the CICD:

.plugin-ci.yaml is needed only for plugins part of [Versatile Data Kit Plugin repo](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins).

The CI/CD is separated in two stages, a build stage and a release stage.
The build stage is made up of a few jobs, all which inherit from the same
job configuration and only differ in the Python version they use (3.7, 3.8, 3.9 and 3.10).
They run according to rules, which are ordered in a way such that changes to a
plugin's directory trigger the plugin CI, but changes to a different plugin does not.
