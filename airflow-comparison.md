## Lineage

Data lineage broadly refers to a collection of tools, practices and approaches which allow the tracking of the flow of data within a data pipeline. Data lineage tools maintain a record of data within its lifecycle, including its source and any transformations applied to it. The main purpose of data lineage is to provide a platform for ensuring data quality, as well as a way of troubleshooting any errors which arise within the data.

OpenLineage is 'an open platform for collection and analysis of data lineage’. It is the defacto industry standard for lineage collection, and it will be the basis for our comparison of lineage capabilities between Airflow and VDK.

Apache Airflow offers support for OpenLineage compliant lineage data collection through the `airflow-openlineage` package; however, out-of-the-box support is only offered for PostgreSQL, Snowflake, MySQL, BigQuery, and the Great Expectations data quality validation framework. Users are expected to implement their own solution or borrow an existing one should they want to collect lineage for queries ran against a different database.
The `airflow-openlineage` package allows the collection of lineage data for individual jobs within a DAG run. However, no DAG-wide lineage can be collected.

Versatile Data Kit offers a lineage collection plugin called vdk-lineage. Thanks to VDK’s extensible architecture, this plugin is endpoint-agnostic, meaning it can collect lineage about queries ran against any current or future SQL database. However, vdk-lineage might struggle to parse more obscure SQL dialects.
VDK offers dedicated lineage collection for Trino and Impala.
VDK can collect lineage about individual queries, as well as entire about Data Jobs - namely job start and end objects and job status - failure or success.



## Templates

We will compare the two platforms based on two forms of templating: the first is the ability of parametrize job executions at runtime, and the second is the ability to build reusable Data Jobs/DAGs which can then be invoked from inside another job/DAG run.

Apache Airflow offers Jinja templating as a method for parametrizing job executions. Jinja is a powerful templating engine based on Django’s templating. It allows the parameterization of arguments passed to operators using runtime variables, as well as more complex expressions.
For more information on Jinja templating in Airflow, refer to the official documentation - https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html?highlight=jinja#templating-with-jinja

Versatile Data Kit offers a mechanism for injecting runtime variables into SQL queries using Data Job arguments. However, this mechanism offers nowhere near the same level of complexity as Jinja templating does.
What makes VDK unique in comparison to Airflow however are Data Job templates. These function essentially as Data Jobs, but can be invoked from inside another Data Job, which allows users to standardise ETL/ELT processes among a large team and/or cut redundancy.
Versatile Data Kit offers out-of-the-box Data Job templates for loading data into SCD1, SCD2 and Periodic Snapshot Fact tables in a Trino or Impala database. Users can also construct their own templates to fit their unique use case.
For more information on Versatile Data Kit’s templating capacities, refer to our Community Demo - https://www.youtube.com/watch?v=HIRt4bX4ddk


## Ingestion

Data ingestion refers to the ability to take some data and send it to a target location.

Versatile Data Kit offers a built-in mechanism for sending data to a configured destination. It provides an API for asynchronous and thread-safe automatic serialization, packaging and sending of data collected from a PEP249-compliant database cursor, a API response call, or any serializable Python iterable object. Additionally, users can configure the parallelism of and frequency at which data is sent, allowing very high throughput of sending data.

Apache Airflow does not provide any out-of-the-box solution for ingesting data; providing support for this is offloaded onto the user.



## Summary

To summarize, Versatile Data Kit and Apache Airflow’s differences arise out of the different abstraction levels they attempt to provide the user with. Airflow is much lower level, more generalized, offering a wider set of capabilities, whereas VDK offers more restricted functionality aimed specifically at providing data engineers with higher level abstractions tailored to their needs.
They are comparable in terms of lineage collection, as they can both be OpenLineage-compliant with the correct extensions, and both offer query-level granularity - VDK offers it directly, and Airflow offers it at the level of DAG jobs, which can be invoked to run individual queries. VDK however also offers job-wide lineage collection, whereas Airflow does not offer any lineage collection on the actual DAG run.
In terms of templating, Airflow offers a more complex templating engine - namely Jinja - for parameterizing job run, while VDK offers job arguments. VDK however offers job templates, which allow users to standardize processes within their organisation and reuse code. VDK also offers built-in templates for common data engineering practices, namely Kimball dimensional modelling.
In terms of ingestion, Versatile Data Kit beats out Airflow with its Ingestion API allowing any Python iterable to be sent to any configured destination using one method invocation.
