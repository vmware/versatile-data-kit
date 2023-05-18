# My shiny new job

Versatile Data Kit feature allows you to implement automated pull ingestion and batch data processing.

# Generative Data Packs
A GDP plugin expands the data you ingest automatically.

# Data expansion
The `vdk-gdp-execution-id` plugin used in [requirements.txt](./requirements.txt) and [config.ini](./config.ini)
automatically expands your dataset with the unique Data Job execution id.
The result is, the dataset produced can be correlated to a particular Data Job execution.

# Run the example
To run the data job locally:
```bash
vdk run gdp-execution-id-example
```

To check the result of data expanded and ingested:
```
% vdk sqlite-query -q "select * from hello_world"
Creating new connection against local file database located at: /var/folders/h3/9ns__d4945qcvkdm2m2vjvqh0000gq/T/vdk-sqlite.db
id            vdk_gdp_execution_id
------------  -----------------------------------------------
Hello World!  a17baca4-4780-4a60-b409-10e8b6fa90de-1682424042
```
Where the `hello_world.id` is being ingested in [20_python_step.py](./20_python_step.py),
and vdk_gdp_execution_id gets added automatically for you.
