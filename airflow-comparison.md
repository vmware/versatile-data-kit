## Intro

What are the differences between these two workload automation engines - and how do they fare in typical data engineering cases? This blog post serves to answer these questions and help you decide which one you should use.

## Functionality Comparison

| Requirement            | Airflow                | Versatile Data Kit     |
|------------------------|------------------------|------------------------|
| Price                  | Free and Open Source   | Free and Open Source   |
| License                | Apache License 2.0     | Apache License 2.0     |
| Language               | Written entirely in Python | CLI written in Python, Control Service written in Java |
| UI                     | Web UI and CLI         | Only a CLI             |
| Runtime variables      | Airflow variables | Properties API     |
| Multitenancy           | Resource-based permissions | Support for separate teams, extensible authorization |
| SSO Support            | No support by default but it can be patched in | Support for Oauth2 |
| Trigger workload execution on new data received | Airflow sensor | No support |
| Deployment API         | None; DAG files must be manually placed within the /dags folder of the Airflow server | VDK Deployment API abstracts away large parts of the DevOps cycle, jobs can be automatically deployed from local files |
| Workload versioning    | None | Automatic Data job versioning upon deployment |
| Automated rollback     | None | Deployment API allows reverting to a previous job version |
| Support for Kimball templates  | None | Built-in Kimball templates available through JobInput API |
| Workload logs          | Available through UI | Available through CLI |
| Monitoring             | Support for StatsD monitoring | Support for Prometheus, Wavefront monitoring |
| Workload scheduling    | Cron scheduling or `datetime.timedelta` object | Cron scheduling |
| Extensibility          | Support for custom operators, connections, sensors | Native extensibility allows custom extensions to insert themselves at any point of the execution |



## Use Case Comparison

### Data Lineage

Data lineage is the process of monitoring, recording, and visualization of the flow of data through a particular data system. For a more detailed description, refer to the [Wikipedia article on the topic](https://en.wikipedia.org/wiki/Data_lineage).

OpenLineage is ['an open platform for collection and analysis of data lineage’](https://openlineage.io/). It will be the basis for our comparison of lineage capabilities between Airflow and VDK.

#### Lineage in Apache Airflow

Apache Airflow offers support for OpenLineage compliant lineage data collection through the `airflow-openlineage` package; however, out-of-the-box support is only offered for PostgreSQL, Snowflake, MySQL, BigQuery, and the Great Expectations data quality validation framework. Users are expected to create their own solution or borrow an existing one should they want to collect lineage for queries ran against a different database.
The `airflow-openlineage` package allows the collection of lineage data for individual jobs within a DAG run. However, no DAG-wide lineage can be collected.

#### Lineage in Versatile Data Kit

Versatile Data Kit offers a lineage collection plugin called `vdk-lineage`. Because of VDK’s extensible architecture, this plugin is endpoint-agnostic, meaning it can collect lineage about queries ran against any current or future SQL database. However, `vdk-lineage` might struggle to parse more obscure SQL dialects.
VDK also offers dedicated lineage collection for Trino and Impala.
VDK can collect lineage about individual queries, no-SQL transformations, ongoing ingestion processes, as well as about entire Data Jobs - namely job start and end objects, as well as the job status - failure or success.



### Templates

Creating Airflow DAGs dynamically is [hacky at best](https://airflow.apache.org/docs/apache-airflow/stable/howto/dynamic-dag-generation.html). VDK offers a much more intuitive approach through the concept of Data Job templates. These function essentially as Data Jobs, but can be invoked from inside another Data Job, which allows users to standardise ETL/ELT processes among a large team and/or cut redundancy.
Versatile Data Kit offers out-of-the-box Data Job templates for loading data into SCD1, SCD2 and Periodic Snapshot Fact tables in a Trino or Impala database. Users can also construct their own templates to fit their unique use case.
For more information on Versatile Data Kit’s templating capacities, refer to [our Community Demo](https://www.youtube.com/watch?v=HIRt4bX4ddk), or [our tutorial on templates](https://github.com/vmware/versatile-data-kit/wiki/SQL-Data-Processing-templates-examples).


### Ingestion

Data ingestion refers to the ability to take some data and send it to a target location.

Versatile Data Kit offers a built-in mechanism for sending data to a configured destination. It provides an API for asynchronous and thread-safe automatic serialization, packaging and sending of data collected from a PEP249-compliant database cursor, a API response call, or any serializable Python iterable object. Additionally, users can configure the parallelism of and frequency at which data is sent, allowing very high throughput of sending data.

Apache Airflow does not provide any out-of-the-box solution for ingesting data; providing support for this is offloaded onto the user.



## Summary

To summarize, Versatile Data Kit and Apache Airflow’s differences arise out of the different abstraction levels they attempt to provide the user with. Airflow is more generalized, offering a less focused set of capabilities, whereas VDK offers more opinionated functionality aimed specifically at providing data engineers with higher level abstractions tailored to their needs. Additionally, Versatile Data Kit is natively extensible, as most of its built-in functionality is implemented through its extensibility mechanism.

They are comparable in terms of lineage collection, as they can both be OpenLineage-compliant with the correct extensions, and both offer query-level granularity - VDK offers it directly, and Airflow offers it at the level of DAG jobs, which can be invoked to run individual queries. VDK however also offers job-wide lineage collection, whereas Airflow does not offer any lineage collection on the actual DAG run.

In terms of templating, VDK offers job templates, which allow users to standardize processes within their organisation and reuse code. VDK also offers built-in templates for common data engineering practices, namely Kimball dimensional modelling.

In terms of ingestion, Versatile Data Kit beats out Airflow with its Ingestion API allowing any Python iterable to be sent to any configured destination using one method invocation.

## Both at the same time

As of [the release of the Airflow provider for Versatile Data Kit](https://medium.com/versatile-data-kit/integrating-apache-airflow-with-versatile-data-kit-41de65a354a2), users are able to operate on Data jobs managed in a deployed instance of the VDK Control Service. This will benefit users who prefer Versatile Data Kit overall for the specific level of abstraction it operates on, but miss the capacity of Airflow to express interdependent workloads.

Additionally, it will benefit users who already have a deployed instance of Airflow and prefer to use it as the main UI for their workload management, but still want to use Versatile Data Kit for its capacity to position workloads on the data path. Now users can develop and use DAGs, where each task triggers a Data job execution through a configured connection to a Control Service.
