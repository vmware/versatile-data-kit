An installed Generative Data Pack plugin automatically expands the data sent for ingestion.

This GDP plugin detects the execution ID of a Data Job running, and decorates your data product with it. So that,
it is now possible to correlate a data record with a particular ingestion Data Job execution ID.

**Each ingested dataset gets automatically expanded with a Data Job execution ID micro-dimension.**
For example:

```json
{
  "product_name": "name1",
  "product_description": "description1"
}
```

After installing `vdk-gdp-execution-id`, one additional field gets automatically appended to your payloads that are
sent for ingestion:

```json
{
  "product_name": "name1",
  "product_description": "description1",
  "gdp_execution_id": "product-ingestion-data-job-1628151700498"
}
```

The newly-added dimension name is configurable.

# Usage

Run

```bash
pip install vdk-gdp-execution-id
```

Create a Data Job and add to its `requirements.txt` file:
```txt
# Python jobs can specify extra library dependencies in requirements.txt file.
# See https://pip.readthedocs.io/en/stable/user_guide/#requirements-files
# The file is optional and can be deleted if no extra library dependencies are necessary.
vdk-gdp-execution-id
```

Reconfigure the ingestion pre-processing sequence to add the plugin name. For example:
```bash
export VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE="vdk-gdp-execution-id"
# or
export VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE="[...,]vdk-gdp-execution-id"
```
_Note: The recommendation is to add this plugin last (at end-of-sequence), due prior plugins may add new data records.
For more info on configurations, see [projects/vdk-core/src/vdk/internal/core/config.py](../../vdk-core/src/vdk/internal/core/config.py)._


Example ingestion Data Job `10_python_step.py`:
```python
def run(job_input: IJobInput):
    # object
    job_input.send_object_for_ingestion(
        payload={"product_name": "name1", "product_description": "description1"},
        destination_table="product")
    # tabular data
    job_input.send_tabular_data_for_ingestion(
        rows=[["name2", "description2"], ["name3", "description3"]],
        column_names=["product_name", "product_description"],
        destination_table="product")
```

In case the `VDK_INGEST_METHOD_DEFAULT` was a relational database,
then you can query the dataset and filter:
```python
# A processing Data Job then filters the ingested dataset by `vdk_gdp_execution_id` column
def run(job_input: IJobInput):
    execution_ids = job_input.execute_query("SELECT DISTINCT vdk_gdp_execution_id FROM product")
    print(execution_ids)
```

# Configuration

Run vdk config-help - search for those prefixed with "GDP_EXECUTION_ID_" to see what configuration options are
available.

# Testing

Testing this plugin locally requires installing the dependencies listed in
vdk-plugins/vdk-gdp-execution-id/requirements.txt

Run

```bash
pip install -r requirements.txt
```

# Example

Find an example data job using `vdk-gdp-execution-id` plugin in [examples/gdp-execution-id-example/](../../../examples/gdp-execution-id-example).
