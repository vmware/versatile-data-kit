
# VEP-NNNN: Your short, descriptive title

* **Author(s):** Paul Murphy (murphp15@tcd.ie), Antoni Ivanov ()
* **Status:** draft

- [Summary](#summary)
- [Glossary](#glossary)
- [Motivation](#motivation)
- [Requirements and goals](#requirements-and-goals)
- [High-level design](#high-level-design)
- [API Design](#api-design)
- [Detailed design](#detailed-design)
- [Implementation stories](#implementation-stories)
- [Alternatives](#alternatives)

## Summary

With the rise in popularity of LLMs and RAG we see VDK as a core component to getting the data where we need it to be.



## Glossary

LLM: Large language model. The most ubiquitous example of this is chatgpt. It is a specialized type of artificial intelligence (AI) that has been trained on vast amounts of text to understand existing content and generate original content.
RAG: Retrival augmented generation. Additional information is passed to the LLM through the prompt. This additional information can help it generate better and more context aware responses.
Vector database: A database which supports storing vectors(arrays of numbers) and doing similarity searches between vectors(cosine distance, dot product etc...).
PGVector: A postgres extension which enables similarity searches in postgres and a vector datatype.


## Motivation

#### Example problem scenario:
A company has a powerful private LLM chatbot.
However they want it to be able to answer questions using the latest version of confluence docs/jira tickets etc...
Retraining every night on the latest tickets/docs is not feasible.
Instead, they opt to use RAG to improve the chatbot responses.

This leaves them with the question.
How do we populate the data?
Steps they need to complete:
1. Read data from confluence/jira
2. Chunk into paragraphs(or something similar)
3. Embed into vector space
4. save Vector and paragraph in vector database
5. remove old information. For example if we are scraping jira every hour and we are writing details to the vector database we need to make sure we clean up all embeddings/chunks which were generated from old versions of the ticket.


#### Benefits to customers:

We want to template this.
We will build a datajob in VDK which reads data from confluence or jira and writes it to a DSM postgres instance with PGVector enabled. A embedding model will be running on a different machine which will be exposed through an API.
We will make requests to the API to create embeddings for us.

After this datajob is running we will create a template from this in which we think customers will be able to adopt to meet their use cases.



## Requirements and goals
1. There should be a single pipelines which given jira/confluence credentials can scrape the source
2. it should chunk up the information, embed it and then save it
3. The systems should be easily configurable
   1. Read from different sources
   2. Different chunks sizes
   3. Different embedders
   4. Extra columns saved in database
4. There should be an example on how to build your own ingestion pipeline
5. Only scraping new data and removing old data must be supported


### Non goals
1. This only populates information into a database that could be used by as RAG system. We don't handle stuffing the actual prompts.

## High-level design
![sequence_diagram.png](sequence_diagram.png)

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
Optionally, describe what are the implementation stories. Link to Milestone or initiative in Github is fine
As part of the implementation make sure to include stories covering release/launch plan, promotional activities before the release,
-->

## Alternatives
<!--
Optionally, describe what alternatives has been considered.
Keep it short - if needed link to more detailed research document.
-->
