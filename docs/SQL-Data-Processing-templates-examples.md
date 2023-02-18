- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [SQL Processing Templates](#sql-processing-templates)
  * [Overwrite Strategy (Slowly changing dimension type 1)](#overwrite-strategy-slowly-changing-dimension-type-1)
  * [Versioned Strategy  (Slowly changing dimension type 2)](#versioned-strategy--slowly-changing-dimension-type-2)
  * [Append Strategy (Fact)](#append-strategy-fact)
  * [Insert Strategy (Fact)](#insert-strategy-fact)
- [What's next](#what-s-next)

# Overview 

Data Jobs can instantiate Data Processing Templates that hide SQL (or Python) specifics behind a more functional, ETL/ELT-oriented interface. The current document presents the Kimball-based slowly changing type template types by example.

# Prerequisites 

The example assumes you have finished [Getting Started](https://github.com/vmware/versatile-data-kit/wiki/Getting-Started)

Data loading templates support depends on the database of choice. 

Currently, there are SQL data processing templates developed for Impala and Trino databases. 
To install trino plugin
```
pip install vdk-trino
```

To install Impala plugin
```
pip install vdk-impala
```

To run a local Trino server (in order to try the templates locally), [install Docker](https://docs.docker.com/get-docker/) and then start the trino db with: 
```
docker run -d -p 18080:8080 --name trino trinodb/trino

# then set following vdk variables: 
export VDK_DB_DEFAULT_TYPE=TRINO
export VDK_TRINO_HOST=localhost
export VDK_TRINO_PORT=18080
export VDK_TRINO_USE_SSL=false

# you can now access local trino server
vdk trino-query -q "show catalogs"
```

# SQL Processing Templates

The VDK offers different data loading templates that abstract over different data loading strategies. Conceptually, a data loading template consumes a source_view located in a source_schema and load the source data in a target_table located in a target_schema.

When building the source_view make sure to follow the best practices for creating efficient queries: Optimizing SQL queries.

##  Overwrite Strategy (Slowly changing dimension type 1)
The SDC1 (slowly changing dimension type 1) strategy overwrites the data in target table with the data defined in the source. This is the recommended strategy for populating [Slowly Changing Dimension (SCD) tables of Type 1](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-1/) in data warehousing ELT jobs.

Assume that you have a target table dw.dim_org that holds dimension data about customer organizations.

|org_id|org_name           |org_type           |company_name     |sddc_limIt|org_host_limit|
|------|-------------------|-------------------|-----------------|----------|--------------|
|1     |mullen@actual.com  |CUSTOMER_MSP_TENANT|actual Master Org|2         |32            |
|2     |johnlocke@other.com|CUSTOMER_POC       |Other            |1         |6             |

The logic in the source view dw.dim_org_view defines the following changes (marked with a different background color). Simply said, the SQL logic of the source view dw.dim_org_view defines what is the "latest state" - is it based on values, timestamp, etc.

|org_id|org_name|org_type|company_name|sddc_limit|org_host_limit|
|-------------|---------------------|---------------------|-----------------------------|-------------------------|---------------------------------|
|2      |johnlocke@other.com|CUSTOMER_POC|VMware            |4                  |16                        |
|3      |lilly.johnsonn@goofys.com|CUSTOMER|Goofy's          |2                  |32                        |
|1      |mullen@actual.com|CUSTOMER_MSP_TENANT|actual Master Org|2                  |32                        |

The API call to execute the template from a Python step looks as follows.

```python
def run(job_input: IJobInput) -> None:
    # ...
    job_input.execute_template(
        template_name='scd1',
        template_args={
            'source_schema': 'dw',
            'source_view': 'dim_org_view',
            'target_schema': 'dw',
            'target_table': 'dim_org',
        },
    )
    # ...
```

For a full list of the required prerequisites and available template parameters, please consult the [scd1 template documentation](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-trino/src/vdk/plugin/trino/templates/load/dimension/scd1).


## Versioned Strategy  (Slowly changing dimension type 2)

The versioned strategy accumulates updates from the data source as versioned records in the target table. This is the recommended strategy for populating [Slowly Changing Dimension (SCD) tables of Type 2](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-2/) in data warehousing ELT jobs.

Assume that you have a target table dw.dim_sddc that holds dimension data about Software Defined Data Centers (SDDCs). So far you have only observed a single version of two distinct SDDC records on the first day of the year.

|sddc_sk|active_from        |active_to          |sddc_id          |updated_by_user_id|state|is_nsxt|cloud_vendor|version|
|-------|-------------------|-------------------|-----------------|------------------|-----|-------|------------|-------|
|sddc01-v01|1.01.19            |31.12.99           |1                |9                 |STOPPED|FALSE  |AWS         |500    |
|sddc02-v01|1.01.19            |31.12.99           |2                |2                 |RUNNING|TRUE   |Azure       |497    |

The surrogate key column sddc_sk that uniquely identifies each record version. In this example, surrogate keys adhere to a fixed pattern sddc{PK}-v{VERSION} for better readability. In practice, the loading template will automatically populate the surrogate keys column with unique random strings. For simplicity, here we have also truncated all timestamps to a YYYY-MM-DD format. The 9999-12-31 value in the active_to column is the biggest timestamp value supported by Impala and indicates that the corresponding record version is open (that is, this is the currently active record version).

On the next day, you observe changes in the values of both SDDCs, and a new version of a third SDDC. These are reflected by populating the data source dw.dim_sddc_updates_view with the following data (we refer to this set of updates as U1).

|updated_at|sddc_id            |updated_by_user_id |state            |is_nsxt|cloud_vendor|version|
|----------|-------------------|-------------------|-----------------|-------|------------|-------|
|2.01.19   |1                  |9                  |**RUNNING**          |FALSE  |AWS         |500    |
|2.01.19   |2                  |2                  |**PAUSED**           |**FALSE**  |Azure       |497    |
|2.01.19   |3                  |7                  |STOPPED          |TRUE   |AWS         |499    |

The API call to integrate the updates from dw.dim_sddc_updates_view into the versioned target table dw.dim_sddc looks as follows.

```python
def run(job_input: IJobInput) -> None:
    # ...
    job_input.execute_template(
        template_name='scd2',
        template_args={
            'source_schema': 'dw',
            'source_view': 'dim_sddc_updates_view',
            'target_schema': 'dw',
            'target_table': 'dim_sddc',
            'id_column': 'sddc_id',
            'sk_column': 'sddc_sk',
            'value_columns': ['updated_by_user_id', 'state', 'is_nsxt', 'cloud_vendor', 'version'],
            'tracked_columns': ['state', 'is_nsxt', 'cloud_vendor', 'version'],
        },
    )
    # ...
```
Upon execution, the target table will look as follows.

|sddc_sk|active_from        |active_to          |sddc_id          |updated_by_user_id|state|is_nsxt|cloud_vendor|version|
|-------|-------------------|-------------------|-----------------|------------------|-----|-------|------------|-------|
|sddc01-v01|1.01.19            |2.01.19            |1                |9                 |STOPPED|FALSE  |AWS         |500    |
|sddc01-v02|2.01.19            |31.12.99           |1                |9                 |RUNNING|FALSE  |AWS         |500    |
|sddc02-v01|1.01.19            |2.01.19            |2                |2                 |RUNNING|TRUE   |Azure       |497    |
|sddc02-v02|2.01.19            |31.12.99           |2                |2                 |PAUSED|FALSE  |Azure       |497    |
|sddc03-v01|2.01.19            |31.12.99           |3                |7                 |STOPPED|TRUE   |AWS         |499    |

The following aspects are automatically handled by the template.

1. Out-of-order updates are generally supported. If you do not have records with matching (id_column, updatet_at_column) values and conflicting value_columns, the order in which the updates are partitioned and ingested as a series of template executions does not affect the final result.
1. An update record with specific (id_column, updated_at_column) values will always replace a target table an existing record version with matching (id_column, active_from_column) values.
1. Adjacent versions of the same record with matching tracked_columns are merged, in the sense that the more recent record version is dropped from the resulting target table.


To illustrate these aspects, let's see what happens if we apply the following set of updates (let's call it U2) to the new version of the target table.

|updated_at|sddc_id            |updated_by_user_id |state            |is_nsxt|cloud_vendor|version|
|----------|-------------------|-------------------|-----------------|-------|------------|-------|
|2.01.19   |1                  |9                  |RUNNING          |FALSE  |AWS         |500    |
|2.01.19   |2                  |2                  |**RUNNING**          |**TRUE**   |Azure       |497    |
|2.01.19   |3                  |5                  |STOPPED          |TRUE   |AWS         |499    |
|3.01.19   |3                  |5                  |**RUNNING**          |TRUE   |AWS         |499    |

After we apply these updates with a second template run, the target table will look like this.


|sddc_sk|active_from        |active_to          |sddc_id          |updated_by_user_id|state|is_nsxt|cloud_vendor|version|
|-------|-------------------|-------------------|-----------------|------------------|-----|-------|------------|-------|
|sddc01-v01|1.01.19            |2.01.19            |1                |9                 |STOPPED|FALSE  |AWS         |500    |
|sddc01-v02|2.01.19            |31.12.99           |1                |9                 |RUNNING|FALSE  |AWS         |500    |
|sddc02-v01|1.01.19            |31.12.99           |2                |2                 |RUNNING|TRUE   |Azure         |497    |
|sddc03-v01|2.01.19            |3.01.19            |3                |5                 |STOPPED|TRUE   |AWS         |499    |
|sddc03-v02|3.01.19            |31.12.99           |3                |5                 |RUNNING|TRUE   |AWS         |499    |

The net result is the sum of the following actions:

* The first update message overwrites sddc01-v2 without a visible effect as both the update message and the record version have the same values (aspect 2).
* The second update message overwrites sddc02-v2 (aspect 2). Since the updated sddc02-v2 version has the same tracked_columns values as sddc02-v1, the template has merged it with its predecessor (aspect 3).
* The third update message overwrites the updated_by_user_id value of sddc02-v2 to 5 (aspect 1).
* The last update message creates a new version sddc03-v02 of the SDDC with sddc_id = 3 and appends it right after the sddc03-v01 version. Note that even if the update messages for sddc03-v01 and sddc03-v02 were swapped in U1 and U2,  the final result would be unchanged (aspect 1).


For a full list of the required prerequisites and available template parameters, please consult the [scd2 template documentation](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-trino/src/vdk/plugin/trino/templates/load/dimension/scd2).

## Append Strategy (Fact)

The append strategy appends a snapshot of records observed between time t1 and t2 from the source view to the target table, truncating all present target table records observed after t1. This strategy can be used for updating [Periodic Snapshot Fact Tables](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/periodic-snapshot-fact-table/) or [transaction fact table](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/transaction-fact-table/) in data warehousing ETL jobs.

As an example, consider a target table dw.fact_sddc_daily that takes a daily snapshot of facts about Software Defined Data Centers (SDDCs).

|dim_sddc_sk|dim_org_id|dim_date_id|host_count|cluster_count|observed_at  |
|-----------|----------|-----------|----------|-------------|-------------|
|sddc01-r01 |1         |18.11.19   |5         |1            |18.11.19 9:00|
|sddc02-r01 |2         |18.11.19   |4         |1            |18.11.19 9:00|
|sddc01-r02 |1         |19.11.19   |5         |1            |19.11.19 9:00|
|sddc01-r01 |2         |19.11.19   |5         |1            |19.11.19 9:00|

The table contains two facts observed at 9AM on 2019-11-18 and two facts observed at the same time one day later.

Assume that your source view dw.fact_sddc_daily_view contains all the facts observed in the last 48 hours. At 9AM on 2019-11-19, it has the following data.

|dim_sddc_sk|dim_org_id|dim_date_id|host_count|cluster_count|observed_at  |
|-----------|----------|-----------|----------|-------------|-------------|
|sddc03-r01 |5         |18.11.19   |18        |4            |18.11.19 9:30|
|sddc01-r02 |1         |19.11.19   |5         |1            |19.11.19 9:00|
|sddc01-r01 |2         |19.11.19   |5         |1            |19.11.19 9:00|
|sddc03-r01 |5         |19.11.19   |18        |4            |19.11.19 9:30|
|sddc01-r03 |1         |20.11.19   |5         |1            |20.11.19 9:00|
|sddc01-r02 |2         |20.11.19   |5         |1            |20.11.19 9:00|
|sddc03-r02 |5         |20.11.19   |20        |4            |20.11.19 9:00|

The source contains two late arriving facts for 2019-11-18 and 2019-11-19 (marked with blue background), the two facts for 2019-11-19 that are already present in the target table (marked with white background), and three new facts for 2019-11-20 (marked with yellow background).

The API call to integrate the snapshot of facts from dw.fact_sddc_daily_view into the target fact table dw.fact_sddc_daily looks as follows.

```python
def run(job_input: IJobInput) -> None:
    # ...
    job_input.execute_template(
        template_name='periodic_snapshot',
        template_args={
            'source_schema': 'dw',
            'source_view': 'fact_sddc_daily_view',
            'target_schema': 'dw',
            'target_table': 'fact_sddc_daily',
            'last_arrival_ts': 'observed_at',
        },
    )
    # ...
```
Upon execution, the target table will look as follows.

|dim_sddc_sk|dim_org_id|dim_date_id|host_count|cluster_count|observed_at  |
|-----------|----------|-----------|----------|-------------|-------------|
|sddc01-r01 |1         |18.11.19   |5         |1            |18.11.19 9:00|
|sddc02-r01 |2         |18.11.19   |4         |1            |18.11.19 9:00|
|sddc03-r01 |5         |18.11.19   |18        |4            |18.11.19 9:30|
|sddc01-r02 |1         |19.11.19   |5         |1            |19.11.19 9:00|
|sddc01-r01 |2         |19.11.19   |5         |1            |19.11.19 9:00|
|sddc03-r01 |5         |19.11.19   |18        |4            |19.11.19 9:30|
|sddc01-r03 |1         |20.11.19   |5         |1            |20.11.19 9:00|
|sddc01-r02 |2         |20.11.19   |5         |1            |20.11.19 9:00|
|sddc03-r02 |5         |20.11.19   |20        |4            |20.11.19 9:00|

For a full list of the required prerequisites and available template parameters, please consult the [snapshot template documentation](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-trino/src/vdk/plugin/trino/templates/load/fact/periodic_snapshot).

## Insert Strategy (Fact)
This template can be used to load raw data from Data Lake to target Table in Data Warehouse. In summary, it appends all records from the source view to the target table. Similar to all other SQL modeling templates there is also schema validation, table refresh and statistics are computed when necessary.

Say there is SDDC-related 'Snapshot Periodic Fact Table' called 'fact_vmc_utilization_cpu_mem_every5min_daily' in 'history' schema. Updating it with the latest raw data from a Data Lake (from source view called 'vw_fact_vmc_utilization_cpu_mem_every5min_daily' in 'default' schema) is done in the following manner:
```python
def run(job_input):
    # . . .
    template_args = {
        'source_schema': 'default',
        'source_view': 'vw_fact_vmc_utilization_cpu_mem_every5min_daily',
        'target_schema': 'history',
        'target_table': 'fact_vmc_utilization_cpu_mem_every5min_daily'
    }
    job_input.execute_template('insert', template_args)
    # . . .
```

The diagram below shows how the data from the source view is inserted into the target table, without checking for duplicate data.
<img width="836" alt="insert_template_2" src="https://user-images.githubusercontent.com/21333266/204796027-0e77631d-dc12-497d-b0c6-df09bbc51a0e.png">


So you should be careful for ensuring no duplicate rows are introduced in the source view you are using.

For a full list of the required prerequisites and available template parameters, please consult the [insert template documentation](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-impala/src/vdk/plugin/impala/templates/load/fact/insert).

(note: currently this is supported only for Impala database)

# What's next

You can find a list of all Versatile Data Kit examples [here](https://github.com/vmware/versatile-data-kit/wiki/Examples).
