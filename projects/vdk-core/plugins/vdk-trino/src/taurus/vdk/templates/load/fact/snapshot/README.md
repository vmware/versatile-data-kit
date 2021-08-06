### Purpose:
Template used to load raw data from Data Lake to target 'Snapshot Accumulating Fact Table' in Data Warehouse.

### Details:
<https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/periodic-snapshot-fact-table/>

### Template Name (template_name):
- "fact/snapshot"

### Template Parameters (template_args):
- target_schema   - Data Warehouse schema, where source raw data is loaded
- target_table    - Data Warehouse table of DW type 'Snapshot Accumulating Fact Table', where source raw data is loaded
- source_schema   - Data Lake schema, where source raw data is loaded from
- source_view     - Data Lake view, where source raw data is loaded from
- last_arrival_ts - Timestamp column, on which increments to target_table are done

### Prerequisites:
In order to use this template you need to ensure the following:
- {source_schema}.{source_view} exists
- {target_schema}.{target_table} exists
- {source_schema}.{source_view} has the exact same schema as {target_schema}.{target_table}
- {last_arrival_ts} is timestamp column suitable for 'Daily Snapshot Accumulating Fact Table' increments

### Sample Usage:
Say there is SDDC-related 'Daily Snapshot Accumulating Fact Table' called 'fact_sddc_daily'.
Updating it with latest raw data from the Data Lake (from source view called 'vw_fact_sddc_daily') is done
in the following manner:

```python
def run(job_input):
    . . .
    fact_name="sddc"
    template_name = "snapshot"
    template_args = {"target_schema": "<target_schema_of_choice>",
                    "target_table": "fact_{}_daily".format(fact_name),
                    "source_schema": "<source_schema_of_choice>",
                    "source_view": "vw_fact_{}_daily".format(fact_name),
                    "last_arrival_ts": "<timestamp_column_of_choice>"}
    job_input.execute_template(template_name, template_args)
    . . .
```
