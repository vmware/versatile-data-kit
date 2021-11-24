## VDK-INGEST-FILE Plugin

This plugin provides functionality to ingest data into a file. It is intended for local testing.

### Usage

To use the plugin, just install it, and set the `method` attribute of `send_object_for_ingestion()`,
and `send_tabular_data_for_ingestion()` functions to _"file"_.

Example:
```python
def run(job_input: IJobInput):
    # Do something to get data for ingestion
    payload = get_some_data()

    # Ingest the data
    job_input.send_object_for_ingestion(payload=payload,
                                        destination_table="aa_test_table",
                                        method="file",
                                        target="name_of_file"
                                        )
```
The above example shows how to ingest json data. In this case, there is only one argument that is required: `payload`.
<br>
It needs to be a json object, and can contain the `destination_table` inside, using the `@table` key. For example:
```
{
    "@table": "destination_table_name",
    "column1": "value1",
    "column2": "value2",
    "column3": "value3",
}
```
The `target` attribute is being used to specify the name of the file, where the data will be ingested. If not specified, it is constructed,
using the model, `table.<creation-timestamp>.json`.<br>
