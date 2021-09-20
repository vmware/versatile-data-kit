### Purpose:

This template can be used to load raw data from a database to target 'Slowly Changing Dimension Type 2' table in a database.
In summary, it accumulates updates from the data source as versioned records in the target table.

### Details:

Explanation of SCD type 2 can be seen here: <https://en.wikipedia.org/wiki/Slowly_changing_dimension#Type_2:_add_new_row>

### Template Name (template_name):

- "scd2"

### Template Parameters (template_args):

- target_schema          - Target schema where the versioned data is stored. Typically, a database schema.
- target_table           - Target table where the versioned data is loaded. Typically, a Slowly Changing Dimension (SCD) of Type 2.
- source_schema          - database schema containing the source view.
- source_view            - database view where source data is loaded from.
- id_column              - Column that holds the natural key of the target table.
- value_columns          - A list of columns from the source that are considered. Present both in the source and the target tables.
- tracked_columns        - A sublist of the value columns that are tracked for changes. Present both in the source and the target tables.
- updated_at_column      - A column containing the update time of a record. Present in the source table.
- sk_column              - A surrogate key column that is automatically generated in the target table.
- active_from_column     - A column denoting the start time of a record in the target table.
- active_to_column       - A column denoting the end time of a record in the target table. Equals `active_to_max_value` if the record is not closed.
- active_to_max_value    - A value denoting an open record in the target table.

### Prerequisites:

In order to use this template you need to ensure the following:

- `{source_schema}`.`{source_view}` exists and consists of the `id_column`, the `value_columns`, and the `updated_at_column`.
- `{target_schema}`.`{target_table}` exists and consists of the following columns (in this order): `{sk_column}`, `{active_from_column}`, `{active_to_column}`, `{id_column}`, and `{value_columns}`.

### Sample Usage:

Say there is SDDC-related 'Slowly Changing Dimension Type 2' target table called 'dim_sddc_h' in 'history' schema.

Integrating a date of existing current records representing current state and adding new state records (from source view called 'vw_dim_sddc_h' in 'default' schema) is done in the following manner:

```python
def run(job_input):
    # . . .
    template_args = {
        'source_schema': 'default',
        'source_view': 'vw_dim_sddc_h',
        'target_schema': 'history',
        'target_table': 'dim_sddc_h',
        'id_column': 'sddc_id',
        'value_columns': ['hosts', 'state', 'is_nsxt', 'cloud_vendor', 'version'],
        'tracked_columns': ['hosts', 'state', 'is_nsxt', 'cloud_vendor', 'version'],
        'updated_at_column': 'updated_at',
        'active_from_column': 'active_from',
        'active_to_column': 'active_to',
        'active_to_max_value': '9999-12-31',
    }
    job_input.execute_template('scd2', template_args)
    # . . .
```
