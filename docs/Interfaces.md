- [Data Jobs development Kit (VDK)](#data-jobs-development-kit--vdk-)
  * [Data Jobs](#Data-Jobs)
  * [CLI for running and developing data jobs](#cli-for-running-and-developing-data-jobs)
  * [Sending data for ingestion from different sources to different destinations](#sending-data-for-ingestion-from-different-sources-to-different-destinations)
  * [Transforming raw data into a dimensional model](#transforming-raw-data-into-a-dimensional-model)
  * [Plugin interfaces](#plugin-interfaces)
  * [Keeping state, configuration and secrets](#keeping-state--configuration-and-secrets)
  * [Reusable Job Templates](#reusable-job-templates)
  * [Parameterized SQL](#parameterized-sql)
- [Control Service](#control-service)
  * [Job Lifecycle API](#job-lifecycle-api)
  * [Job Deployment API](#job-deployment-api)
  * [Job Execution API](#job-execution-api)
  * [GraphQL Jobs Query API](#graphql-jobs-query-api)
  * [Teams support](#teams-support)
  * [SSO support](#sso-support)
  * [Access Control](#access-control)
  * [Auditing](#auditing)
  * [Monitoring metrics](#monitoring-metrics)

<!--  Generated using http://ecotrust-canada.github.io/markdown-toc
-->

Versatile Data Kit provides the following interfaces to enable building data pipelines:


### Data Jobs development Kit (VDK)

It enables engineers to develop, test and run [[Data Jobs|dictionary#Data Job]] on a local machine.
It comes with common functionality for data ingestion and processing like:

#### Data Jobs

Data Jobs are the central interface around which all others go around. It represents single unit of work - it can be a project (job can have many files) or a single SQL query. This is where the main business logic is being written. They provide ability to write SQL only transformation or complex python steps and run them both locally and in cloud.

#### CLI for running and developing data jobs 

CLI can be used to run data job locally or can be attached to [[debugger|example-using-debugger]] to debug jobs.
Users can use plugins to mock almost any part of the data job enabling easier debugging.

See more in [[hello world example|Getting Started]]

For more also check CLI help after [installing the SDK](https://github.com/vmware/versatile-data-kit/wiki/Installation#install-sdk) using vdk --help` or `vdk <command-name> --help`

#### Sending data for ingestion from different sources to different destinations

It's easy to built plugins to send data to different destinations like Snowlfake, Reshift or ETL tools like Fivetran/Stitch.

See more in [SDK IIngester](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L90) and [SDK IIngesterPlugin](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/plugin/plugin_input.py#L164)

See list of currently developed plugins in [plugins directory](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins)

#### Transforming raw data into a dimensional model 

Some common templates VDK provide or Slowly Changing Dimenstion type 1 and 2. 

Users can also build multiple templates enabling them to easily establish common ways for transforming data.

See more in [SDK ITemplate](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L286)
and for new template can be registered as plugins using [ITemplateRegistry](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/plugin/plugin_input.py#L82) 

See usage examples in [Data Processing Templates Examples](https://github.com/vmware/versatile-data-kit/wiki/SQL-Data-Processing-templates-examples) 

#### Plugin interfaces

Extensibility system has been designed to be able to plugin at almost all points of execution of the CLI.
It's meant to make it easy to customize CLI for any organization use-case. 
It's meant to also make it easy to integrate with any open source tool - like _DBT_ for SQL only transformations, 
or _dagster_ for functional dataflow or _great_expectations_ for data quality checks.

See more in the [[Plugin README|https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-plugins/README.md]]

#### Keeping state, configuration and secrets

Properties are variables passed to your data job and can be updated by your data job.

You can use them to:

- Control the behavior of jobs and pipelines.
- Store state you want to re-use. For example, you can store last ingestion timestamp for incremental ingestion job.
- Keep credentials like passwords, API keys. 


See more in [Properties REST API](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/projects/model/apidefs/datajob-api/api.yaml#L792)
See more in [SDK IProperties](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L11)
See more in [SDK Plugin interface for properties](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/plugin/plugin_input.py#L49)

#### Reusable Job Templates

Templates are pieces of reusable code, which is common to use cases of different customers of Versatile Data Kit.
Templates are executed in the context of a Data Job
They provide an easy solution to common tasks like loading data to a data warehouse.

See more in [SDK ITemplateRegistry](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/plugin/plugin_input.py#L82)
See more in [SDK ITemplate](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L286)

See usage examples in [Data Processing Templates Examples](https://github.com/vmware/versatile-data-kit/wiki/SQL-Data-Processing-templates-examples) 

#### Parameterized SQL

SQL steps can be parameterized 

```sql
select * from {table_name}
```
And table_name will be automatically replaced by looking at Data Job Arguments or Data Job Properties


### Control Service 

Control Service provides REST API which enables creating, deploying, managing and executing Data Jobs in Kubernetes runtime environment. 

It also provides CLI for interacting with it in more user friendly 

#### Job Lifecycle API

The API reflects the usual Data Application (or in our case Data Job) lifecycle that we've observed:
1. Create a new data job (webhook to further configure job in common way -e.g authorize its creation, setup permissions, etc).
2. Develop and run the data job locally.
3. Deploy data job in cloud runtime enviornment to run on scheduled basis.
4. Monitor and operate Job


See more in [API docs](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/projects/model/apidefs/datajob-api/api.yaml)

#### Job Deployment API

Data Jobs can be automatically versioned and deployed and managed. 
The API can be used through CLI currently. 

The API is designed (but not implemented) to support strict separation of config from code. 
When from single source code there could be multiple deploymensts with different configuration

API is meant to allow integration with UI (e.g UI IDE) to enable non-engineers to contribute.

See more in [Deployment API docs](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/projects/model/apidefs/datajob-api/api.yaml)

#### Job Execution API

Execution API enables managing execution of data jobs. It keep relations between which version of the code was used
and what configuration it was started with. 
It's also designed to be the integration point with Workflow tools like Airflow.

See more in [Execution API docs](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/projects/model/apidefs/datajob-api/api.yaml)

#### GraphQL Jobs Query API

List Data Jobs with GraphQL like query enabling to inspect job definitions, 
deployments and executions for your team or across team. 
The API is designed to make it easy to develop UI on top of it.

See more in [Jobs Query API docs](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/projects/model/apidefs/datajob-api/api.yaml)

#### Teams support

Group data jobs that belong to a single team together. Can also apply authorization rules using [access control webhooks](#access-control-and-auditing-capabilities)
Enable multiple teams to both collaborate and yet work independently - think [Distributed Data Mesh](https://martinfowler.com/articles/data-mesh-principles.html)

#### SSO support

It support Oauth2 based authorization of all operations enabling easy to integrate with company SSO.

See more in [security section of Control Service Helm chart](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/projects/helm_charts/pipelines-control-service/values.yaml#L280)

#### Access Control

Access control can be configured using Oauth2-based on claim values. See more in the [helm chart configuration](https://github.com/vmware/versatile-data-kit/blob/c2565b4975818f2cf62f3dfb356feb7d229ad24d/projects/control-service/projects/helm_charts/pipelines-control-service/values.yaml#L395)

For more complex use cases Access Control Webhooks enable the creation of custom rules for who is allowed to do what operations in the Control Service. See more in [Authorization webhook configuration](https://github.com/vmware/versatile-data-kit/blob/c2565b4975818f2cf62f3dfb356feb7d229ad24d/projects/control-service/projects/helm_charts/pipelines-control-service/values.yaml#L391)


#### Auditing
One can subscribe for webhooks for all operations executed by Control Service

See more in [Webhooks configuration](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/projects/helm_charts/pipelines-control-service/values.yaml#L226)

#### Monitoring metrics

Control Service is designed to easily integrate with different monitoring systems like Prometheus, Wavefront, etc. 
It's easiest to integrate with Prometheus due to its tight collaboration with Kubernetes.

See list of metrics supported in [here](https://github.com/vmware/versatile-data-kit/tree/main/projects/control-service/projects/helm_charts/pipelines-control-service#metrics)
See more in [monitoring configuration](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/projects/helm_charts/pipelines-control-service/values.yaml#L391)
