# Huggingface

<a href="https://pypistats.org/packages/vdk-huggingface" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-huggingface.svg" alt="monthly download count for vdk-huggingface"></a>

Versatile Data Kit (VDK) plugin for integrating with Huggingface as both a data source and a target.
This plugin allows you to ingest data payloads into a Huggingface repository and makes it easier to work with datasets stored in Huggingface.


## Usage

```
pip install vdk-huggingface
```

The functionality adds new ingestion method "huggingface" which can be used like that:

```python
job_input.send_object_for_ingestion(data, method="huggingface")
```


### Configuration

(`vdk config-help` is useful command to browse all config options of your installation of vdk)

| Name                | Description                                                                 | (example)  Value        |
|---------------------|-----------------------------------------------------------------------------|-------------------------|
| HUGGINGFACE_TOKEN   | HuggingFace API token for authentication. Get one from HuggingFace Settings | ""                      |
| HUGGINGFACE_REPO_ID | HuggingFace Dataset repository ID                                           | "username/test-dataset" |



### Build and testing

```
pip install -r requirements.txt
pip install -e .
pytest
```

In VDK repo [../build-plugin.sh](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/build-plugin.sh) script can be used also.


#### Note about the CICD:

.plugin-ci.yaml is needed only for plugins part of [Versatile Data Kit Plugin repo](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins).

The CI/CD is separated in two stages, a build stage and a release stage.
The build stage is made up of a few jobs, all which inherit from the same
job configuration and only differ in the Python version they use (3.7, 3.8, 3.9 and 3.10).
They run according to rules, which are ordered in a way such that changes to a
plugin's directory trigger the plugin CI, but changes to a different plugin does not.
