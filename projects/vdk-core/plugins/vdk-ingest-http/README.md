### VDK-INGEST-HTTP Plugin

This plugin provides functionality to ingest data over http.

### Usage

To use the plugin, just install it, and set the `method` attribute of `send_object_for_ingestion()`,
and `send_tabular_data_for_ingestion()` functions to _"http"_.

Example:
```python
def run(job_input: IJobInput):
    # Do something to get data for ingestion
    payload = get_some_data()

    # Ingest the data
    job_input.send_object_for_ingestion(payload=payload,
                                        destination_table="aa_test_table",
                                        method="http",
                                        target="http://example.com/data-source"
                                        )
```
The above example shows how to ingest json data. In this case, there are three arguments that are required: `payload`,
`method` and `target`. This would be fixed in the future, so that only `payload` would be required.
<br>
The payload needs to be a json object, and should contain the `destination_table` inside, using the `@table` key. For example:
```
{
    "@table": "destination_table_name",
    "column1": "value1",
    "column2": "value2",
    "column3": "value3",
}
```
The `method` attribute needs to be provided for the time being.
<br>
The `target` attribute should specify the url endpoint, where the data will be ingested.
