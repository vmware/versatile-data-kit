### Purpose:

Template used to load raw data from a Data Lake to target 'Slowly Changing Dimension Type 2' table in a Data Warehouse.
This is very simple implementation whic overrides rows based on updated timestamp and ID. It's generally not recommended to use.
Prefer to use ["sdc2" template instead](https://github.com/vmware/versatile-data-kit/wiki/SQL-Data-Processing-templates-examples#versioned-strategy--slowly-changing-dimension-type-2)

### Details:

Explanation of SCD type 2 can be seen here: <https://en.wikipedia.org/wiki/Slowly_changing_dimension#Type_2:_add_new_row>

### Template Name (template_name):

- "scd2_simple"

### Template Parameters (template_args):

- target_schema   - SC Data Warehouse schema, where target data is loaded
- target_table    - SC Data Warehouse table of DW type 'Slowly Changing Dimension Type 2', where target data is loaded
- source_schema   - SC Data Lake schema, where source raw data is loaded from
- source_view     - SC Data Lake view, where source raw data is loaded from
- start_time_column      - Column that holds the start time of the period for which a record is valid
- end_time_column        - Column that holds the end time of the period for which a record is valid
- end_time_default_value - Default value for end time column used to indicate whether this is the current state of the record, e.g. '2999-01-01T00:00:00Z'
- surrogate_key_column   - Column that holds unique id permanently bound to the time period defined by that row of the slowly changing dimension table. Useful for efficient joins with other fact tables.
- id_column              - Column that holds the natural key of the target table.

### Prerequisites:

In order to use this template you need to ensure the following:
- {source_schema}.{source_view} exists
- {target_schema}.{target_table} exists
- The schema of {target_schema}.{target_table} must begin with a string column (used to hold the surrogate key) followed by all columns of {source_schema}.{source_view}.
- {source_schema}.{source_view} must contain all columns specified in the Parameters section.
- In {source_schema}.{source_view}, for records which represent current state their end_time value must be the same as the value provided as end_time_default_value

### Sample Usage:

Say there is SDDC-related 'Slowly Changing Dimension Type 2' target table called 'dim_sddc_h' in 'history' schema.
Updating end date of existing current records representing current state and adding new state records (from source view called 'vw_dim_sddc_h' in 'default' schema) is done in the following manner:

```python
def run(job_input):
    # . . .
    template_args = {
        'source_schema': 'default',
        'source_view': 'vw_dim_sddc_h',
        'target_schema': 'history',
        'target_table': 'dim_sddc_h',
        'start_time_column': '<name_of_start_time_column>',
         'end_time_default_value': '2999-01-01T00:00:00Z',
         'end_time_column': '<name_of_end_time_column>',
         'surrogate_key_column': '<name_of_surrogate_key_column>',
         'id_column': '<name_of_id_column>'
    }
    job_input.execute_template('load/dimension/scd2', template_args)
    # . . .
```
