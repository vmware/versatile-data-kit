The following is a collection of notes made during and after research into integrating Great Expectations into Versatile Data Kit. They are not intended to be read as a holistic document, and might contradict each other in places.

## **Brief overview of great_expectations**

Great_expectations(GE) is a Data Quality platform/library which aims to, among other purposes, help data scientists validate their data against a particular set of tests(Expectations), which are essentially data tests. Additionally, it offers automatic data documentation, data validation failure notifications, data test versioning, and connection to data systems. It is primarily intended to be used through bash scripting and Python.

 

## **GE use cases in VDK**

A potential GE use case in VDK is applying Expectations on some data set before ingestion. This way, data scientists can integrate data quality checks in their scripts which can notify them in the case of bad/non-typical data.

The plugin would work in the following way:

The user would need to have configured an Expectation suite in advance, which is comprised of the data validation tests, against which we will be testing our data;
Then, using the run_job hook we can access the payload to be ingested and validate it against the expectation suite before the actual job, and then print the results to console, or notify them by email (using the emails from the job config) in case if the validation fails.



## **Update on GE plugin implementation**

Currently, vdk-core does not offer a plugin hook which exposes the payload which is to be ingested. Whether such a hook will be implemented is currently undecided. The current implementation uses a wrapper around the job_input.send_object_for_ingestion method which first performs some data quality validation before executing the original method.

The current validation is a single line checking the number of columns; more complicated validation can possibly be performed by extending the send_object_for_ingestion wrapper with a Checkpoint parameter(from https://docs.greatexpectations.io/en/latest/reference/core_concepts.html : A Checkpoint facilitates running a validation as well as configurable Actions such as updating Data Docs, sending a notification to your team about validation results, or storing a result in a shared S3 bucket. The Checkpoint makes it easy to add Great Expectations to your project by tracking configuration about what data, Expectation Suite, and Actions should be run when.) which is configured by the user. Possible extra functionality could be a Checkpoint generator which can construct a Checkpoint from the job configuration.



## **Review of intended UX process**

1. The user constructs a set of tests for their data - these could be validating that none of the data is null, or that the values in a particular column are unique, etc. The exact syntax for this set of tests is unclear yet - ideally this would be a .yml file, as they are the preferred approach for configurations, although implementational restrictions might require something different. In the case where there are multiple payloads with different semantics to be ingested in the same job, there must be some way of configuring which tests are applied to which payload. Possible approaches are considered further on.
2. The user runs the data job using an instance of VDK with the vdk-great-expectations plugin installed. This plugin would either implement a wrapper around the ingestion function, or utilise some plugin hook which is not yet implemented, and apply whichever tests in the set are appropriate for that payload. Assuming that the payload passes, it gets ingested as normally, and if it does not, the execution will terminate with an appropriate exception - for example, one stating that the execution has stopped due to the test failure, and will include the exact failure description as provided by Great Expectations.




## **Possible approaches for separating tests according to payload**

1. Unique set of tests for each individual data job step - this could be key-value map mapping step name to set of tests, featuring only the steps which ingest data. This assumes that all the payloads ingested by a particular step will always have the same semantics, which is not necessarily true.
2. Unique set of tests for each individual column name - similar to the previous approach, however this time mapping column name to set of tests. The issue with this approach is that different tables might have columns with the same name, which however require different tests.
3. Unique set of tests according to target table name - we can reasonably assume that two payloads intended for the same table will have the same semantics. However, this presupposes that we know in advance which is the target table, which might not be true is some cases.
4. ??? 