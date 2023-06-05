### Purpose:

This template can be used to load raw data from Data Lake to target Table in Data Warehouse. In summary, it appends all records from the source view to the target table. Similar to all other SQL modeling templates there is also schema validation, table refresh and statistics are computed when necessary.

### Template Name (template_name):

- "insert"

### Template Parameters (template_args):

- target_schema   - Data Warehouse schema, where target data is loaded
- target_table    - Data Warehouse table of DW type table, where target data is loaded
- source_schema   - Data Lake schema, where source raw data is loaded from
- source_view     - Data Lake view, where source raw data is loaded from
- check           - (Optional) Callback function responsible for checking the quality of the data
- staging_schema  - (Optional) Schema where the checks will be executed. If not provided target_schema will be used as default

### Prerequisites:

In order to use this template you need to ensure the following:
- {source_schema}.{source_view} exists
- {target_schema}.{target_table} exists
- {source_schema}.{source_view} has the exact same schema as {target_schema}.{target_table}

### Sample Usage:

The diagram below shows how the data from the source view is inserted into the target table, without checking for duplicate data.
<img width="836" alt="insert_template_2" src="https://user-images.githubusercontent.com/21333266/204796027-0e77631d-dc12-497d-b0c6-df09bbc51a0e.png">
So you should be careful for ensuring no duplicate rows are introduced in the source view you are using.

Say there is SDDC-related 'Snapshot Periodic Fact Table' called 'fact_vmc_utilization_cpu_mem_every5min_daily' in 'history' schema.
Updating it with the latest raw data from a Data Lake (from source view called 'vw_fact_vmc_utilization_cpu_mem_every5min_daily' in 'default' schema) is done in the following manner:

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

### Example

See all templates in [our example documentation](https://github.com/vmware/versatile-data-kit/wiki/SQL-Data-Processing-templates-examples).
