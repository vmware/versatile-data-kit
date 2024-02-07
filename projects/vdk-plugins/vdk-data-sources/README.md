# data-sources

<a href="https://pypistats.org/packages/vdk-data-sources" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-data-sources.svg" alt="monthly download count for vdk-data-sources"></a>

Enables Versatile Data Kit (VDK) to integrate with various data sources by providing a unified interface for data ingestion and management.

The data-sources project is a plugin for the Versatile Data Kit (VDK). It aims to simplify data ingestion from multiple sources by offering a single, unified API. Whether you're dealing with databases, REST APIs, or other forms of data, this project allows you to manage them all in a consistent manner. This is crucial for building scalable and maintainable data pipelines.


## Usage

### Installation

```
pip install vdk-data-sources
```

### Concepts


#### Data Source
A Data Source is a central component responsible for establishing and managing a connection to a specific set of data. It interacts with a given configuration and maintains a stateful relationship with the data it accesses. This stateful relationship can include information such as authentication tokens, data markers, or any other form of metadata that helps manage the data connection. The Data Source exposes various data streams through which data can be read.

#### Data Source Stream
A Data Source Stream is an abstraction over a subset of data in the Data Source. It can be thought of as a channel through which data flows.
Each Data Source Stream has a unique name to identify it and includes methods to read data from the stream. Streams cna be ingested in parallel.

Examples:
- In a database (like postgres), each table could be a separate stream.
- In a message broker like Apache Kafka, each topic within Kafka acts as a distinct Data Source Stream.
- In an REST API , the data source is the HTTP base URL (http://xxx.com). The data stream could be each different endpoint (http://xxx.com/users, http://xxx/admins)

Reading from the stream yields a sequence of Data Source Payloads

#### Data Source Payload
The Data Source Payload is a data structure that encapsulates the actual data along with its metadata. The payload consists of four main parts:

Data: containing the core data that needs to be ingested (e.g in database the table content)
Metadata: A dictionary containing additional contextual information about the data (for example timestamps, environment specific metadata, etc.)
State: Contains the state of the data soruce stream as of this payload.
For example in case of incremental ingestion from a database table it would contain the value of a incremental key columns
(le.g updated_time column in teh table) which can be used to restart/continue the ingestion later.


### Configuration

(`vdk config-help` is useful command to browse all config options of your installation of vdk)

### Example

To build your own data source you can use [this data source](./src/vdk/plugin/data_sources/auto_generated.py) as an example or reference

To register the source use [vdk_data_sources_register hook](./src/vdk/plugin/data_sources/hook_spec.py)

Then you can use it in a data job like this:

```python
def run(job_input: IJobInput):
    source = SourceDefinition(id="auto", name="auto-generated-data", config={})
    destination = DestinationDefinition(id="auto-dest", method="memory")

    with DataFlowInput(job_input) as flow_input:
        flow_input.start(DataFlowMappingDefinition(source, destination))
```

or in config.toml file
```toml
[sources.auto]
name="auto-generated-data"
config={}
[destinations.auto-dest]
method="memory"
[[flows]]
from="auto"
to="auto-dest"
```

```python
def run(job_input: IJobInput):
    with DataFlowInput(job_input) as flow_input:
        flow_input.start_flows(toml_parser.load_config("config.toml"))
```

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
