
# VEP-994: Jupyter Notebook Integration

* **Author(s):** Duygu Hasan(hduyg@vmware.com)
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

<!--
Short summary of the proposal. It will be used as user-focused
documentation such as release notes or a (customer facing) development roadmap.
The tone and content of the `Summary` section should be
useful for a wide audience.
-->

## Glossary

* VDK: https://github.com/vmware/versatile-data-kit/wiki/dictionary#vdk

## Motivation

Versatile Data Kit provides utilities for developing SQL and Python data jobs and deploying them in the cloud. However, the only interface it has for development is the CLI.

As a workload users install their own IDE (PyCharm, for example) locally and configure it with VDK. However, VDK is used by people who do not want to nor need to learn how to work with CLI and install and configure IDEs.
Moreover, many of our users are data scientists who work with big data, and they prefer working with notebooks especially for visualizing and testing. After some interviews we did, and demos we watched, we saw that users switch from IDEs to notebooks in order to see how the data changes (it is easier for them to do it in notebooks since it provides better visualization) and they do some changes on the code there (they are testing small sections which can lead to changes in small sections) which leads to copy pasting the new code from the notebook to the IDE. The whole process of switching from one place to another is inconvenient and tedious. It would be much easier for the users to just open a familiar UI and enter their SQL queries or Python code, without using the CLI and without copy pasting code from one place to another.

Furthermore, currently VDK users need to rerun the whole Data job again every time they do a small change on the code, or a single unit fails. This could be rather time-consuming since the ELT process might be slow. For example, extracting and loading data again only for a small change in transformation.
By integrating VDK with Jupyter we want to make VDK more accessible and  present those users better experience and with their natural choice and make their VDK onboarding process much easier

Jupyter is chosen because it is  very well-known among the data community, it is de-facto the current standard – see:
1. https://towardsdatascience.com/top-4-python-and-data-science-ides-for-2021-and-beyond-3bbcb7b9bc44#:~:text=JupyterLab,hacks%20for%20more%20advanced%20use
2. https://businessoverbroadway.com/2020/07/14/most-popular-integrated-development-environments-ides-used-by-data-scientists/


## Requirements and goals

### Requirements
Legend (terms and table are based on Pragmatic Marketing recommendations):
* Problem - a discrete pain or issue that has been observed within the target market segment. In the below table it's a short summary name of the problem.
* Use Scenario - a description of a problem. Includes a detailed description of the typical situation that causes this problem to occur and possibly current results.
* Evidence - the percentage of interviewed users who have mentioned the problem.
* Impact - how much impact does the problem have on their work (high/moderate/low).

|                 Problem                  |                                                                                                                  Use Scenario                                                                                                                  | Evidence |  Impact  |
|:----------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:--------:|:--------:|
 |             Working with CLI             |                                                                As data engineers we do not have much experience with CLI, we need to learn how to use CLI in order to use VDK.                                                                 |   70%    |   high   |
 |  IDEs are not convenient for debugging   |                             As data engineers, we often use Jupyter as a debugging tool instead of using IDE debuggers because of the big data we work with. This leads to copy pasting code from IDE to Jupyter.                              |   70%    |   high   |
 |  IDEs are not convenient for for tests   |                              As data engineers, we test code in Jupyter quite often because small changes are more visible in graphics, we run small code blocks in many cells and watch how the graphics change.                              |   70%    | moderate |
 | Moving to production from notebook files | As data engineers we  need to switch from notebooks to python files every time we are moving to production which is done either by copy pasting or using automated functions of Jupyter but might lead to syntax errors and bad coding habits. |   50%    |   low    |
 |    Rerun whole job for small changes     |                                                              As data engineers,when we use VDK, we need to rerun the whole job again every time we do a small change on the code.                                                              |   40%    ||     |     |
|     Rerun whole job for failing step     |                                                                       As data engineers, when we use VDK, we need to rerun the whole job again every time a step fails.                                                                        |   40%    ||     |     |
|    Too many SQL files in one data job    |                 As data engineers,we need to write one SQL statement per file which leads to creating files for simple delete/create queries and we end up creating a lot of SQL files every time we need a complex data job.                  |   30%    |   low    |


### Goals
* The users should have easy access to Jupyter notebook that is integrated with the VDK.
* Provide UI experience  for VDK which will decrease the use of CLI and solve the problems of switching from IDE to Notebook and from Notebook to IDE.
* The solution should be installable in centralized instance of jupyterhub or jupyterlab.
* The solution should provide a way to rerun only failing/changed steps and the steps after them.
* The number of files needed for job steps should be minimized.



## High-level design
![screenshot](/Users/hduygu/Desktop/Screenshot.png)

JupyterLab is the next-generation user interface for Project Jupyter offering all the familiar building blocks of the classic Jupyter Notebook (notebook, terminal, text editor, file browser, rich outputs, etc.) in a flexible and powerful user interface.
Fundamentally, JupyterLab is designed as an extensible environment. JupyterLab extensions can customize or enhance any part of JupyterLab.

The proposed design describes the solution for creating a Jupyter UI for VDK. For this purpose, a JupyterLab extension will be implemented, and it will give us the chance to create graphical elements like buttons and widgets – alternatives of currently used CLI commands. An iPython package will also be implemented to export VDK variables. This package will be imported to JupyterLab, and they will be accessible from there.



#### Comparing the options with requirements matrix



#### Deployment

* Users can click deploy from within the notebook and the job would be deployed in VDK runtime ("cloud")
* Users should see the status of the deployed jobs
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
