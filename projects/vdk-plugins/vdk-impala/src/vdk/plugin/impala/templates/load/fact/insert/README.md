### Purpose:

This template can be used to load raw data from Data Lake to target 'Insert Fact Table' in Data Warehouse.
In summary, it appends a snapshot of records observed between time t1 and t2 from the source table to the target table. After that inserts the rows from the source table.

### Details:

<https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/periodic-snapshot-fact-table/>

### Template Name (template_name):

- "insert"

### Template Parameters (template_args):

- target_schema   - SC Data Warehouse schema, where target data is loaded
- target_table    - SC Data Warehouse table of DW type 'Snapshot Periodic Fact Table', where target data is loaded
- source_schema   - SC Data Lake schema, where source raw data is loaded from
- source_view     - SC Data Lake view, where source raw data is loaded from

### Prerequisites:

In order to use this template you need to ensure the following:
- {source_schema}.{source_view} exists
- {target_schema}.{target_table} exists
- {source_schema}.{source_view} has the exact same schema as {target_schema}.{target_table}
- {last_arrival_ts} is timestamp column suitable for 'Insert Fact Table' increments

### Sample Usage:

Say there is SDDC-related 'Snapshot Periodic Fact Table' called 'fact_vmc_utilization_cpu_mem_every5min_daily' in 'history' schema.
Updating it with the latest raw data from a Data Lake (from source view called 'vw_fact_vmc_utilization_cpu_mem_every5min_daily' in 'default' schema) is done in the following manner:

```python
def run(job_input):
    # . . .
    template_args = {
        'source_schema': 'default',
        'source_view': 'vw_fact_vmc_utilization_cpu_mem_every5min_daily',
        'target_schema': 'history',
        'target_table': 'fact_vmc_utilization_cpu_mem_every5min_daily',
        'last_arrival_ts': 'updated_at',
    }
    job_input.execute_template('load/fact/insert', template_args)
    # . . .
```

### Example

See full example of how to use the template in [our example documentation](https://github.com/vmware/versatile-data-kit/wiki/SQL-Data-Processing-templates-examples#append-strategy-periodic-snapshot-fact).