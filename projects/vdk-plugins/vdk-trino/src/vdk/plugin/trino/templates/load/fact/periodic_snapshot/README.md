### Purpose:

This template can be used to load raw data from a database to target 'Snapshot Periodic Fact Table' in a database.
In summary, it appends a snapshot of records observed between time t1 and t2 from the source table to the target table,
truncating all present target table records observed after t1.

### Details:

<https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/periodic-snapshot-fact-table/>

### Template Name (template_name):

- "periodic_snapshot"

### Template Parameters (template_args):

- target_schema   - database schema, where target data is loaded
- target_table    - database table of type 'Snapshot Periodic Fact Table', where target data is loaded
- source_schema   - database schema, where source raw data is loaded from
- source_view     - database view, where source raw data is loaded from
- last_arrival_ts - Timestamp column, on which increments to target_table are done

### Prerequisites:

In order to use this template you need to ensure the following:
- {source_schema}.{source_view} exists
- {target_schema}.{target_table} exists
- {source_schema}.{source_view} has the exact same schema as {target_schema}.{target_table}
- {last_arrival_ts} is timestamp column suitable for 'Snapshot Periodic Fact Table' increments

### Sample Usage:

Say there is SDDC-related 'Snapshot Periodic Fact Table' called 'fact_sddc_daily' in 'history' schema.
Updating it with the latest raw data from a database (from source view called 'vw_fact_sddc_daily' in 'default' schema) is done in the following manner:

```python
def run(job_input):
    # . . .
    template_args = {
        'source_schema': 'default',
        'source_view': 'vw_fact_sddc_daily',
        'target_schema': 'history',
        'target_table': 'fact_sddc_daily',
        'last_arrival_ts': 'updated_at',
    }
    job_input.execute_template('periodic_snapshot', template_args)
    # . . .
```
