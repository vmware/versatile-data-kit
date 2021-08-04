### Purpose:
Template used to load raw data from the Data Lake to target 'Slowly Changing Dimension Type 1' table in the Data Warehouse.

### Details:
  <https://en.wikipedia.org/wiki/Slowly_changing_dimension#Type_1:_overwrite>

### Template Name (template_name):
- "scd1"

### Template Parameters (template_args):
- target_schema   - Data Warehouse schema, where source raw data is loaded
- target_table    - Data Warehouse table of DW type 'Slowly Chaning Dimension Type 1', where source raw data is loaded
- source_schema   - Data Lake schema, where source raw data is loaded from
- source_view     - Data Lake view, where source raw data is loaded from

### Prerequisites:
In order to use this template you need to ensure the following:
- {source_schema}.{source_view} exists
- {target_schema}.{target_table} exists
- {source_schema}.{source_view} has the exact same schema as {target_schema}.{target_table}

### Sample Usage:
Say there is SDDC-related 'Slowly Changing Dimension Type 1' target table called 'dim_sddc'.
Updating it with the latest raw data from the Data Lake (from source view called 'vw_dim_sddc') is done in the following manner:
```python
def run(job_input):
    # . . .
	dimension_name="sddc"
	template_args = {"target_schema": "<target_schema_of_choice>",
	                 "target_table": "dim_{}".format(dimension_name),
	                 "source_schema": "<source_schema_of_choice>",
	                 "source_view": "vw_dim_{}".format(dimension_name)}
	job_input.execute_template("scd1", template_args)
    # . . .
```
