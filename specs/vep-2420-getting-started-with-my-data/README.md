
# VEP-2420: VDK Getting Started with My Data

* **Author(s):** Paul Murphy (paulm2@vmware.com), Antoni Ivanov (aivanov@vmware.com)
<!-- * **Status:** draft | implementable | implemented | rejected | withdrawn | replaced -->
* **Status:** draft


- [VEP-2420: VDK Getting Started with My Data](#vep-2420-getting-started-with-my-data)
  - [Summary](#summary)
  - [Glossary](#glossary)
  - [Motivation](#motivation)
    - [Poor assistance around configuration options](#Poor-assistance-around-configuration-options)
    - [Layers of abstraction aren't clear](#Layers-of-abstraction-are-not-clear)
    - [Poor documentation around secrets/properties](#Poor-documentation-around-secrets-and-properties)
    - [Not trivial to run in the IDE](#Not-trivial-to-run-in-the-IDE)
    - [Reliant on env variables](#Reliant-on-env-variables)
  - [Requirements and goals](#requirements-and-goals)
  - [High-level design](#high-level-design)
  - [API design](#api-design)
  - [Detailed design](#detailed-design)
  - [Implementation stories](#implementation-stories)
  - [Alternatives](#alternatives)

## Summary

Users struggle to get started with their own data in VDK.
When evaluating a data platform like VDK one of the first actions is often to connect it to your own data sources and play around with it.
Given that this is not a trivial task on VDK it most likely turns a lot of prospective users off.
The issues range from data jobs being difficult to configure to jobs bring difficult to run.  
On the completion of this initiative user should be able to use VDK to play around with their data in <10 minutes. 

## Glossary

## Motivation
At the moment, VDK users face multiple challenges related to using their own data in VDK.
Based on user feedback we've received, these can be split into 5 categories.

### Poor assistance around configuration options

VDK documents all config and all config can be seen with 'vdk config-help'.
However despite this there are a number of issues which make it difficult to configure VDK.


1. Users are expected to configure their job using a config.ini file. Ini files are not popular in the industry
2. Sections are confusing
ini files support sections (https://en.wikipedia.org/wiki/INI_file#Sections).
Within VDK there are a few different sections, [vdk],[job], [owner].
Newer properties always go in the [vdk] section.
It's not clear which properties go in which section. In fact some properties can exist in different sections and will have the same result.
3. There is no validation on the file at run time to make sure all properties exist. Ideally the system should throw an error if there are properties in the file which don't actually exist.
4. There is no IDE assistance. Frameworks like spring support autocomplete in their property and yaml files.

### Not obvious what properties do
Below are the properties most jobs need to set.
```bash
export VDK_DB_DEFAULT_TYPE=SQLITE
export VDK_INGEST_METHOD_DEFAULT=sqlite
export VDK_INGEST_TARGET_DEFAULT=vdk-sqlite.db
export VDK_SQLITE_FILE=vdk-sqlite.db
```

Ingest is a confusing term.
It is a totally reasonable explanation to think that the ingestion database is the database where we want to ingest data from wheras it means the database we want to ingest data into.
Its not obvious what impact having setting DB_DEFAULT_type has.

### Layer's of abstraction are not clear

The VDK advertises its self as being a useful tool for reading and writing to databases(It helps with retries etc...).
However if you are reading from a database to ingest the data into VDK you actually don't use VDK SDK to connect to the source database.
This can be seen in this tutorial: https://github.com/vmware/versatile-data-kit/wiki/Ingesting-data-from-DB-into-Database
This is extremely confusing. I would expect that I use the postgres plugin to read the data.


### Poor documentation around secrets and properties

When first starting with VDK and your own data you will need to provide VDK with passwords/username/etc. to connect to you data source.
There is a file based implementation of the properties provider. This is not heavily enough advertised in the getting started docs.
Furthermore there is no file based implementation of the secrets provider. So on even the most trivial example of reading data the user is left wondering how to handle secrets.

### Not trivial to run in the IDE

There is actually great documentation on how to get this working.
But it needs to be included as the first line of the getting started section as this is the first thing that should be done after creating a job.

### Reliant on env variables
In our tutorials we encourage users to set ingest destination using env variables: https://github.com/vmware/versatile-data-kit/wiki/Ingesting-data-from-DB-into-Database.
This is bad because:
1. How env variables are set is different on linux and windows. This results in our tutorial having less support for windows users as we write our tutorials assuming mac/linux users
2. Works on my computer problems. If they complete a tutorial and check it into git, someone else won't be able to run it without knowing they need to set a list of env variables
3. Poor IDE support. If they set the properties in the terminal and run examples they will see everything running ok. then they run it in their IDE and it won't work because it isn't picking up the properties. This is painful experince for developers
4. they might restart their computer and the example won't run and they can't remember why


## Requirements and goals

1. Easily finding out which properties to set for a given task
   1. During development
      1. The IDE should provide auto complete of properties
      2. TODO

## High-level design

<!--
All the rest sections tell **how** are we solving it?

This is where we get down to the specifics of what the proposal actually is.
This should have enough detail that reviewers can understand exactly what
you're proposing, but should not include things like API designs or
implementation. What is the desired outcome and how do we measure success?

Provide a valid UML Component diagram that focuses on the architecture changes
implementing the feature. For more details on how to write UML Component Spec -
see https://en.wikipedia.org/wiki/Component_diagram#External_links.

For every new component on the diagram, explain which goals does it solve.
In this context, a component is any separate software process.

-->


## API design

<!--

Describe the changes and additions to the public API (if there are any).

For all API changes:

Include Swagger URL for HTTP APIs, no matter if the API is RESTful or RPC-like.
PyDoc/Javadoc (or similar) for Python/Java changes.
Explain how does the system handle API violations.
-->


## Detailed design
<!--
Dig deeper into each component. The section can be as long or as short as necessary.
Consider at least the below topics but you do not need to cover those that are not applicable.

### Capacity Estimation and Constraints
    * Cost of data path: CPU cost per-IO, memory footprint, network footprint.
    * Cost of control plane including cost of APIs, expected timeliness from layers above.
### Availability.
    * For example - is it tolerant to failures, What happens when the service stops working
### Performance.
    * Consider performance of data operations for different types of workloads.
       Consider performance of control operations
    * Consider performance under steady state as well under various pathological scenarios,
       e.g., different failure cases, partitioning, recovery.
    * Performance scalability along different dimensions,
       e.g. #objects, network properties (latency, bandwidth), number of data jobs, processed/ingested data, etc.
### Database data model changes
### Telemetry and monitoring changes (new metrics).
### Configuration changes.
### Upgrade / Downgrade Strategy (especially if it might be breaking change).
  * Data migration plan (it needs to be automated or avoided - we should not require user manual actions.)
### Troubleshooting
  * What are possible failure modes.
    * Detection: How can it be detected via metrics?
    * Mitigations: What can be done to stop the bleeding, especially for already
      running user workloads?
    * Diagnostics: What are the useful log messages and their required logging
      levels that could help debug the issue?
    * Testing: Are there any tests for failure mode? If not, describe why._
### Operability
  * What are the SLIs (Service Level Indicators) an operator can use to determine the health of the system.
  * What are the expected SLOs (Service Level Objectives).
### Test Plan
  * Unit tests are expected. But are end to end test necessary. Do we need to extend vdk-heartbeat ?
  * Are there changes in CICD necessary
### Dependencies
  * On what services the feature depends on ? Are there new (external) dependencies added?
### Security and Permissions
  How is access control handled?
  * Is encryption in transport supported and how is it implemented?
  * What data is sensitive within these components? How is this data secured?
      * In-transit?
      * At rest?
      * Is it logged?
  * What secrets are needed by the components? How are these secrets secured and attained?
-->


## Implementation stories
<!--
Optionally, describe what are the implementation stories (eventually we'd create github issues out of them).
-->

## Alternatives
<!--
Optionally, describe what alternatives has been considered.
Keep it short - if needed link to more detailed research document.
-->
