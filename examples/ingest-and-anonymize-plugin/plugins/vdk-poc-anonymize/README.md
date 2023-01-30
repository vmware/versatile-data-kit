# POC Anonymization plugin

**This is a sample plugin used in an example/tutorial for creating plugins. It is not a real plugin.**

**The below README is a sample README of what is usually expected of a real plugin README**




POC Anonymization plugin automatically all data being ingested using Versatile Data Kit
![anonymization-poc-plugin](https://user-images.githubusercontent.com/2536458/175018358-f671df82-8459-47a9-8dce-85f79e68133a.png)


## Usage

```
pip install vdk-poc-anonymize
```

### Configuration

(`vdk config-help` is useful command to browse all config options of your installation of vdk)

| Name | Description | (example)  Value |
|---|---|---|
| anonymization_fields | What fields to be ingested should be anonymized.  In format of { "table/entity_name": [ <list of entity fields/columns> ] } | { "table": [ "col", "mol" ] } |
| ingest_payload_preprocess_sequence | Must be set to "anonymize" either in job config or as environment variable  or global vdk options of the VDK Server (Control Service).  | anonymize |


## Build and testing

```
pytest
```
