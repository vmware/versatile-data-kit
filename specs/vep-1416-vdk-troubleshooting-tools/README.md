
# VEP-1416: VDK Troubleshooting Tools

* **Author(s):** Andon Andonov (andonova@vmware.com)
* **Status:** draft


  - [Summary](#summary)
  - [Glossary](#glossary)
  - [Motivation](#motivation)
  - [Requirements and goals](#requirements-and-goals)
  - [High-level design](#high-level-design)
  - [API design](#api-design)
  - [Detailed design](#detailed-design)


## Summary

-----
This VEP outlines the changes that would need to be introduced to provide users and Versatile Data Kit administrators with tools to troubleshoot data jobs, which are deployed in a kubernetes cluster. These tools will be provided through a dedicated plugin, which will be configurable and extendable, so more functionality could be added in the future.

The initial troubleshooting capability introduced, is the ability to do a thread dump of the python process and send it to a specific endpoint.


## Glossary

-----
- VDK: https://github.com/vmware/versatile-data-kit/wiki/dictionary#vdk
- Plugins: https://github.com/vmware/versatile-data-kit/wiki/dictionary#vdk-plugins
- Data Job: https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job
- Data Job Execution: https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job-execution
- Data Job Deployment: https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job-deployment
- Kubernetes: https://kubernetes.io/
- Prometheus: https://prometheus.io/docs/introduction/overview/


## Motivation

-----
When a data job, which is deployed in a kubernetes cluster, fails with an error, the VDK Deployment administrator can troubleshoot it either through the exposed Prometheus metrics or by looking at the job's logs. This works in most cases, but fails when there are issues with the logging service, some dependency does not propagate its logs, or when the configuration of the environment has been changed.

In such cases, there are a couple of approaches that can be taken:

1. An execution of the job can be triggered manually, and the administrator can connect to the cluster directly and either examine the logs as they are produced, or attach to the pod of the data job and troubleshoot it remotely. This has the limitation that the person doing the troubleshooting needs to have access to the kubernetes cluster, and even then the container in which the data job is running may not have all the utilities (editor, program for monitoring of running processes, etc.) to allow for proper troubleshooting. Additionally, it may not be possible for the data job to be run off its schedule due to business concerns, in which case the users/admins would need to wait for the job's next scheduled execution.
2. The data job can be executed locally, so that the user/admin can have complete control over the environment. This again has the drawback that off-schedule execution of the data job may not be possible. Also, in case the issue is with some environment configuration or system dependency, the error may not be reproducible locally, which can make troubleshooting even more difficult.

To allow for easier troubleshooting of errors with data jobs, a special plugin will be introduced, which will provide capabilities to do a thread dump and either log the contents or stored locally, where it can be examined by the owner of the data job or by the team responsible for the VDK deployment. The plugin could also be extended in the future with other debugging capabilities.


## Requirements and goals

-----
### Goals

* **Introduce a vdk-jobs-troubleshooting plugin**

* **Provide capability to do a thread dump**
  - An administrator wants to get a thread dump of the data job process for troubleshooting purposes. For example, a user deploys a data job and after some time the job starts failing without any apparent reason. The administrator needs to be able to get a thread dump, so they are able to properly investigate the root cause for the issue.

### Non-Goals

* **Additional troubleshooting tools are not planned as part of this proposal.**
* **The thread-dump feature would not be exposed to users/data job owners.**


## High-level design

-----

![plugin_diagram.png](diagrams/plugin_diagram.png)

For the proposed design, a vdk-jobs-troubleshooting plugin will be introduced. The plugin will start a http server instance, which will allow users to obtain a thread dump (which will also be printed in the logs) for further troubleshooting.


## API design

-----

No changes to the public API.


## Detailed design

-----

### vdk-jobs-troubleshooting Plugin
The plugin will act as a toolbox, where data job troubleshooting tools will be implemented. As part of this proposal, only a thread-dump utility will be implemented. It will start a local web server, which will attach to port 8080 and, depending on configuration, will allow for the dump to be logged as part of normal logging processes, or a user can do port-forwarding to the data job pod and examine the contents of the thread data.

![plugin_details.png](diagrams/plugin_details.png)

The main configuration variable for this plugin would be:
* VDK_TROUBLESHOOT_UTILITIES_TO_USE, which will accept a comma-separated list of string literals with the troubleshooting utilities that will be used, e.g., `"utility1,utility2,..."`.


### Availability
The plugin will be part of the vdk installation, so the same availability constraints apply. The http server will be running in a separate process, but it will still be available as long as the data job pod is running. In case of issues with the logging service, the http server would still be able to log the thread-dump locally in the data job pod.

### Security and Permissions
As the http server will run locally within the data job pod, no ports would be exposed externally. This means that only users who have the necessary permissions to connect to the kubernetes cluster would be able to connect to the server itself.

In cases, where the thread dump is logged through the logging service, the security considerations for the general execution logs will apply.
