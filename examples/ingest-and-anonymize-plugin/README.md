# Jobs and Anonymization POC

This repositories contains sample jobs and plugin used to demonstrate how to create automated data pipeline:

![ingest-and-anonymization-poc](https://user-images.githubusercontent.com/2536458/182483829-51ad1618-f36d-4ac1-93ca-d3d6a1c7085a.png)

1. Ingest data in XML format . We ingest currency rate of USD to Polish Zloty for last year from Polish Bank APIs (but could be any source)
2. Prior to writing the data to a cloud storage it de-personalize it based on configuration (provided by plugin). The POC uses sha256 but that easily could be changed (see [anonymizer.py](https://github.com/vmware/versatile-data-kit/blob/main/examples/ingest-and-anonymize-plugin/plugins/vdk-poc-anonymize/src/vdk/plugin/anonymize/anonymizer.py) )
3. The data is written into relation database as different tables (again configurable)

This repo structure:
- Directory "jobs" contains a sample data job that can be implemented by data engineers.
- Directory "plugins" contains a plugin expected to be developed and once installed it will be automatically applied for all data jobs created by all data engineers in the company.
