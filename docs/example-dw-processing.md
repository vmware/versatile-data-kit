> :warning: IN PROGRESS (Not working yet)

# **Prerequisites**
- Read the [**Getting Started Guide**](getting_started.md)
- Completed [](example-ingest-rest-api.md)
- Have [**VDK installed**](install.md)

# Overview
In this example - we will use the Data Jobs Development Kit (**VDK)** to develop a processing Data Job (read the [User Guide](https://confluence.eng.vmware.com/display/SuperCollider/Data+Pipelines+User+Guide) for explanation of the types of data jobs). The job will read data from the Super Collider Data Lake, process it (this is the 'transform' phase in the ETL terminology) and write the result to the Super Collider Data Warehouse.

You can follow along and run this example Data Job on your computer to get first hand experience with Data Jobs or you can use the code as a template and extend it to make a Data Job that processes some data of your own.

We will take a look into a Data Job with name: **example-process-in-star-schema**.

Below we will be describing the overwrite (scd1) template strategy. Please see other template strategies for updating warehouse tables in [**Data Pipelines - Example use of templates](https://confluence.eng.vmware.com/pages/createpage.action?spaceKey=SUPCR&title=Data+Pipelines+-+Example+use+of+templates)**


We will process data ingested by the [Ingest from REST API](example-ingest-rest-api.md) job. This job reads **users** objects from a public REST service and ingests them into the Data Lake.
Our processing job will simplify the data by taking only the properties we need (id, name, username, email) and write the simplified users to the Data Warehouse.

## **Source**
The table in the Data Lake that we will process is **sc\_code\_samples\_\_users** and contains data in the following format:

**sc\_code\_samples\_\_users** 

<!---
Use some markdown table generator like https://www.tablesgenerator.com/markdown_tables
-->
| **id** | **name**      | **username** | **email** | **address\_street** | **address\_suite** | **address\_city** | **address\_zipcode** | **address\_geo\_lat** | **address\_get\_lng** | **phone**             | **website**                            | **company\_name** | **company\_catchPhrase**               | **company\_bs**             |
|--------|---------------|--------------|-----------|---------------------|--------------------|-------------------|----------------------|-----------------------|-----------------------|-----------------------|----------------------------------------|-------------------|----------------------------------------|-----------------------------|
| 1      | Leanne Graham | Bret         |           | Kulas Light         | Apt. 556           | Gwenborough       | 92998-3874           | -37.3159              | 81.1496               | 1-770-736-8031 x56442 | [hildegard.org](http://hildegard.org/) | Romaguera-Crona   | Multi-layered client-server neural-net | harness real-time e-markets | 

## **Destination**
The resulting simplified **users** data will be recorded in the Data Warehouse in **dim\_users** table.

| **id** | **name**         | **username** | **email** |
|--------|------------------|--------------|-----------|
| 1      | Leanne Graham    | Bret         |           |
| 2      | Ervin Howell     | Antonette    |           |
| 3      | Clementine Bauch | Samantha     |           |

# File Structure
The data job consists of the following elements:



**example-process-in-star-schema**

```
example-process-in-star-schema
├── 10_create_processing_view.sql
├── 20_create_target_dimension.sql
├── 30_execute_template.py
└── config.ini
example-process-in-star-schema.keytab
```
# Setup
We will create a view that will be the essence of the processing task.
In this case, the view will simply get a subset of the users schema with the properties we need.

```sql
CREATE VIEW IF NOT EXISTS super_collider.vw_dim_users AS
SELECT id, name, username, email FROM history_staging.sc_code_samples__users
```
We will then create the table in the Data Warehouse where we will record the simplified objects.

```sql
CREATE TABLE IF NOT EXISTS super_collider.dim_users (id string, name string, username string, email string) stored as parquet
```

# Processing
Finally, we will execute the template to load the data into the Data Warehouse. The template uses **Slowly Changing Dimension Type 1** (new data overwrites old one) to insert the data (<https://en.wikipedia.org/wiki/Slowly_changing_dimension#Type_1:_overwrite>)

**10\_execute\_template.py**

```python
def run(job_input: IJobInput):
 
    template_args = {'target_schema': 'super_collider',
                     'target_table': 'dim_users',
                     'source_schema': 'super_collider',
                     'source_view': 'vw_dim_users'}
 
    job_input.execute_template(template_name='scd1', template_args=template_args)
```

For a full list of the required prerequisites and available template parameters, please consult [the load.dimension.scd1 template documentation](https://todo/templates/scd1/README.md).

# Execute

Data jobs are executed with the 'vdk' command (you should have first installed VDK in your python virtualenv):

```bash
vdk run example-process-in-star-schema
```

Upon successful local execution of the job, you will see output similar to this one:
```
2019-10-17 10:48:11,110=1571298491[VDK] example-process-in-star-schema [INFO ] vacloud.vdk.command_run              command_run.py:88   run             [OpId:1571298370.144615]- Execution of example-process-in-star-schema completed successfully. Result is:
{
  "dataset_name": "example-process-in-star-schema",
  "execution_id": "1571298370.144615",
  "start_time": "2019-10-17T07:46:10Z",
  "end_time": "2019-10-17T07:48:11Z",
  "steps_list": [
    {
      "name": "10_execute_template.py",
      "type": "python",
      "start_time": "2019-10-17T07:46:10Z",
      "end_time": "2019-10-17T07:48:11Z",
      "status": "success",
      "details": null
    }
  ]
}
2019-10-17 10:48:11,110=1571298491[VDK] example-process-in-star-schema [INFO ] vacloud.vdk.command_run              command_run.py:91   run             [OpId:1571298370.144615]- Data Job execution finished successfully.
```

# Result
After the execution of this data job, we will have the simplified **users** from the external REST API written in the Data Warehouse. Since we are using [Slowly Changing Dimension Type 1](https://en.wikipedia.org/wiki/Slowly_changing_dimension#Type_1:_overwrite), the new records will replace the old ones.

# Source Code
The complete source of the data job can be seen in the data jobs repository: <https://todo/tree/master/example-process-in-star-schema>.






