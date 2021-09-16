### Purpose:

This template can be used to load raw data from a database to target 'Slowly Changing Dimension Type 1' table in a database.
In summary, it overwrites the target table with the source data.

### Details:
  <https://en.wikipedia.org/wiki/Slowly_changing_dimension#Type_1:_overwrite>

### Template Name (template_name):

- "scd1"

### Template Parameters (template_args):

- target_schema   - database schema, where target data is loaded
- target_table    - database table of type 'Slowly Changing Dimension Type 1', where target data is loaded
- source_schema   - database schema, where source raw data is loaded from
- source_view     - database view, where source raw data is loaded from

### Prerequisites:

In order to use this template you need to ensure the following:
- {source_schema}.{source_view} exists
- {target_schema}.{target_table} exists
- {source_schema}.{source_view} has the exact same schema as {target_schema}.{target_table}

### Sample Usage:

Say there is SDDC-related 'Slowly Changing Dimension Type 1' target table called 'dim_sddc' in 'history' schema.
Updating it with the latest raw data from a database (from source view called 'vw_dim_sddc' in 'default' schema) is done in the following manner:

```python
def run(job_input):
    # . . .
    template_args = {
        'source_schema': 'default',
        'source_view': 'vw_dim_sddc',
        'target_schema': 'history',
        'target_table': 'dim_sddc',
    }
    job_input.execute_template("scd1", template_args)
    # . . .
```
