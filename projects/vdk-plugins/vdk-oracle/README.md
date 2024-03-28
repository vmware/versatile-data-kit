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
