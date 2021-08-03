### Purpose:

Template used to load raw data from Data Lake to target 'Slowly Changing Dimension Type 2' table in Data Warehouse.

### Details:

Explanation of SCD type 2 can be seen here: <https://en.wikipedia.org/wiki/Slowly_changing_dimension#Type_2:_add_new_row>

### Template Name (template_name):

- "scd2"

### Template Parameters (template_args):

- target_schema          - Target schema where the versioned data is stored. Typically a Data Warehouse (DW) schema.
- target_table           - Target table where the versioned data is loaded. Typically a Slowly Changing Dimension (SCD) of Type 2.
- source_schema          - Data Lake schema containing the source view.
- source_view            - Data Lake view where source data is loaded from.
- id_column              - Column that holds the natural key of the target table.
- value_columns          - A list of columns from the source that are considered errors. Present both in the source and the target tables.
- tracked_columns        - A sublist of the value columns that are tracked for changes. Present both in the source and the target tables.
- updated_at_column      - A column containing the update time of a record. Present in the source table. Optional (default value is "updated_at").
- sk_column              - A surrogate key column that is automatically generated in the target table. Optional (default value is "sk").
- active_from_column     - A column denoting the start time of a record in the target table. Optional (default value is "active_from").
- active_to_column       - A column denoting the end time of a record in the target table. Equals `active_to_max_value` if the record is not closed. Optional (default value is "active_to").
- active_to_max_value    - A value denoting an open record in the target table. Optional (default value is "9999-12-31").

### Prerequisites:

In order to use this template you need to ensure the following:

- `{source_schema}`.`{source_view}` exists and consists of the `id_column`, the `value_columns`, and the `updated_at_column`.
- `{target_schema}`.`{target_table}` exists and consists of the following columns (in this order): `{sk_column}`, `{active_from_column}`, `{active_to_column}`, `{id_column}`, and `{value_columns}`.

### Sample Usage:

Say there is SDDC-related 'Slowly Changing Dimension Type 2' target table called 'dim_sddc_h'.

Integrating a date of existing current records representing current state and adding new state records (from source view called 'vw_dim_sddc_h') is done in the following manner:

```python
def run(job_input):
    # . . .
    template_name = 'scd2'
    template_args = {
        'source_schema': 'history',
        'source_view': 'sddc_h_updates',
        'target_schema': 'vmc_dw',
        'target_table': 'sddc_h',
        'id_column': 'sddc_id',
        'value_columns': ['hosts', 'state', 'is_nsxt', 'cloud_vendor', 'version'],
        'tracked_columns': ['hosts', 'state', 'is_nsxt', 'cloud_vendor', 'version'],
    }
    job_input.execute_template(template_name, template_args)
    # . . .
```
