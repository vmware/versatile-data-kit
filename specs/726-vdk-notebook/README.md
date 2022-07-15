
# VEP-726: VDK Notebook

* **Author(s):** Antoni Ivanov (aivanov@vmware.com)
* **Status:** draft

## Summary

Jupyter notebook is very popular environment used by data engineers and data scientist
to develop data and ML models. And currently VDK does not provide any IDE like capabilities.

This VEP proposes an enhancement that will integrate VDK with Jupyter.
This way we would provide natural IDE
in which engineers can make use of all features of VDK within a well known environment for them.
Engineers can write their data job steps directly in the Jupyter notebook and execute them.
With single click then deploy them on the cloud and then monitor them through the jupyter UI as well.


## Motivation


Versatile Data Kit provides utilities for developing SQL and Python data jobs and deploying them in the cloud.
However, the only interface it has for development is the CLI (command-line interface).

As a workaround users need to install their own IDE (PyCharm, for example) locally and configure it with VDK.
While some users would be fine with that,
VDK is also used by users who do not want to nor need to learn how to work with the CLI or install and configure IDEs.


It would be much easier for them to just open a familiar UI and enter their SQL queries (or Python code),
click “Run” to test it, and finally click “Deploy” to send the data job to the cloud.
To that end, Jupyter is very well known among the data community.
It is de-facto the current standard - see [link 1](https://towardsdatascience.com/top-4-python-and-data-science-ides-for-2021-and-beyond-3bbcb7b9bc44#:~:text=JupyterLab,hacks%20for%20more%20advanced%20use.)
and [link 2](https://businessoverbroadway.com/2020/07/14/most-popular-integrated-development-environments-ides-used-by-data-scientists/)
).
Thus, integrating VDK with Jupyter would present those users with their natural choice and make their VDK onboarding process that much easier.



## Requirements and Goals

### Goals

* Users can install new plugin vdk notebook and new command to start local jupyter notebook
For example user would install jupyter pluigin with `pip install vdk-jupyter`
and then they will be able to start local jupyter instance with `vdk start-jupyter` which will run local instance
This is simply making it more integrated experience for new users. User can install vdk-jupyter in existing jupyter installation.

* The plugin should be installable in server (centerilized) instance of jupyterhub or jupyterlab

Once installed they get following capabilities

#### Development of jobs

* Users can develop and run each step of the job in the notebook
  They will have direct access to job_input in the cells.
  They can have vdk cells
```python
job_input.ingest(xxx)
```
or SQL
```python
%%sql
select * from x
```

And cell that are ignored when running data job (e.g EDA type of cells?)
```
%% non-vdk
```

#### Option 1: Data Job import/export

* VDK Data Job can be imported in Jupyter notebook either from locally using a new button in the jupyter UI "Import Job"
* VDK Data Job can be downloaded from VDK runtime and imported as well.
* Users can export back the data job .

#### Option 2: notebook as a job step

* The jupyuter notebook can be a step in VDK e.g 10_jupyter.ipynb for example.

#### Deployment

* Users can click deploy from within the notebook and the job would be deployed in VDK runtime ("cloud")
* Users should see the status of the deployed jobs


## API Design
<!--
All the rest sections tell **how** are we solving it?

Describe the changes and additions to the public API (if there are any).

For all API changes:

Include Swagger URL for HTTP APIs, no matter if the API is RESTful or RPC-like. PyDoc/Javadoc (or similar) for Python/Java changes.
Explain how does the system handle API violations.
-->

## High-level design

<!--
Provide a valid UML Component diagram that focuses on the architecture changes implementing the feature.
For more details on how to write UML Component Spec - see https://en.wikipedia.org/wiki/Component_diagram#External_links.

For every new component on the diagram, explain which use cases does it solve. In this context, a component is any separate software process.
-->

## Detailed design
<!--
Dig deeper into each component. Consider the following topics.

* Capacity Estimation and Constraints
    * Cost of data path: CPU cost per-IO, memory footprint.
    * Cost of control plane including cost of APIs, expected timeliness from layers above, cost of implementation.
* Availability.
    * For example - is it tolerant to failures, What happens when the service stops working
* Performance.
    * Consider performance of data operations for different types of workloads. Consider performance of control operations
    * Consider performance under steady state as well under various pathological scenarios,
      e.g., different failure cases, partitioning, recovery.
    * Performance scalability along different dimensions, e.g. #objects, network properties (latency, bandwidth), number of data jobs, processed/ingested data, etc.
* Define (database) data model changes
* Telemetry and monitoring changes.
* Configuration changes.
* Upgrade / Downgrade Strategy (especially if it might be breaking change).
* Troubleshooting and operability.
* Test Plan

-->

## Security and Permissions
<!--
How is access control handled?
* Is encryption in transport supported and how is it implemented?
* What data is sensitive within these components? How is this data secured?
    * In-transit?
    * At rest?
    * Is it logged?
* What secrets are needed by the components? How are these secrets secured and attained?
-->

## Implementation Stories
<!--
Describe what are the implementation stories (eventually we'd create github issues out of them).
-->

## Alternatives
<!--
Optionally, describe what alternatives has been considered.
Keep it short - if needed link to more detailed research document.
-->
