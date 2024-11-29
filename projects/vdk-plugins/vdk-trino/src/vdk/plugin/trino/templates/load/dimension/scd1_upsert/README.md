### Purpose:

This template can be used to load raw data from a database to target 'Slowly Changing Dimension Type 1' table with specific implementation.
In summary, it upserts the target table with the source data.

### Template Name (template_name):

- "scd1_upsert"

### Template Parameters (template_args):

- target_schema   - database schema, where target data is loaded
- target_table    - database table where target data is loaded
- source_schema   - database schema, where source raw data is loaded from
- source_view     - database view, where source raw data is loaded from
- id_column       - column that will be used for tracking which row should be updated and which inserted
- check           - (Optional) Callback function responsible for checking the quality of the data. Takes in a table name as a parameter which will be used for data validation
- staging_schema  - (Optional) Schema where the checks will be executed. If not provided target_schema will be used as default

### Database (database):
- if only one trino db is being used then value will be "trino"
- if multiple databases being used then based on database requirement value will be given.

### Prerequisites:

In order to use this template you need to ensure the following:
- {source_schema}.{source_view} exists
- {target_schema}.{target_table} exists
- {source_schema}.{source_view} has the exact same schema as {target_schema}.{target_table}
- Both {source_schema}.{source_view} and {target_schema}.{target_table} have unique key that will be used for the {id_column} argument

### Sample Usage:

Say there is SDDC-related target table called 'dim_sddc' in 'history' schema which has unique key column called 'dim_sddc_id'.
Upserting it with the latest raw data from a database (from source view called 'vw_dim_sddc' in 'default' schema) is done in the following manner:

```python
def run(job_input):
    # . . .
    template_args = {
        'source_schema': 'default',
        'source_view': 'vw_dim_sddc',
        'target_schema': 'history',
        'target_table': 'dim_sddc',
        'id_column': 'dim_sddc_id'
    }
    job_input.execute_template("scd1_upsert", template_args, database="trino")
    # . . .
```
