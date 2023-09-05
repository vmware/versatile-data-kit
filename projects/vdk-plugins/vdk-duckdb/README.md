# duckdb

Simple description of my project.

TODO: what the project is about, what is its purpose


## Usage

```
pip install vdk-duckdb
```

### Configuration

(`vdk config-help` is useful command to browse all config options of your installation of vdk)

| Name | Description | (example)  Value |
|---|---|---|
| dummy_config_key | Dummy configuration | "Dummy" |

### Example

TODO

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
