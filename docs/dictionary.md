# Versatile Data Kit Terms Dictionary

### Data Job
Data processing unit that allows data engineers to implement automated pull ingestion (E in ELT) or batch data transformation into Data Warehouse (T in ELT).

### Data Job Step 

A single unit of work for a Data Job. Usually this is SQL or Python file. Steps are executed in an alphanumerical order of their file names. Plugins can provide different types of steps or change execution order.

### Data Job Source 
All Python, SQL files, and requirements.txt (and others) of the Data Job. These are versioned and tracked per job.

### Data Job Properties 
Any saved state, configuration, and secrets of a Data Job. Those are tracked per deployment. They can be used across different job executions. In the future, they should also be versioned.<br>
They can be accessed using [IProperties python interface](https://gitlab.eng.vmware.com/product-analytics/data-pipelines/vdk/-/blob/master/src/vacloud/api/job_input.py#L8) within a data job or CLI vdk properties command.

### Data Job Deployment 
Deployment takes both the build/code and the deployment-specific properties, builds and packages them and once a Data Job is deployed, it is ready for immediate execution in the execution environment. It can be scheduled to run periodically.

### Data Job Run
### Data Job Attempt

Single run of a Data Job. Data Job run is usually referred to when a Data Job is executed locally. A job may have multiple attempts (or runs) in a job execution. 
See [Data Job Execution](#data-job-execution).<br>
See [opid-executionid-attemptid diagram](#opid-executionid-attemptid)

### Data Job Execution  
An instance of a running Data Job deployment is called an execution.

Data Job execution can run a Data Job one or more times. If a run (attempt) fails due to a platform error, the job can be automatically re-run (this is configurable by Control Service operators)

This is applicable only for executions in the "Cloud" (Kubernetes). Local executions always comprise of a single attempt.

See [Data Job Attempt](#data-job-attempt).<br>
See [opid-executionid-attemptid diagram](#opid-executionid-attemptid)

### Data Job Arguments
A Data Job Execution or Data Job Run can accept any number of arguments when started. Those are unique for each execution/run. They are usually used when Execution is triggered manually by user or when user is developing locally.

### VDK 
VDK is Versatile Data Kit SDK. 

It provides common functionality for data ingestion and processing and CLI for managing lifecycle of a Data Job (see [Control Service](#Control-Service))
 
### Control Service

The "backend" part. It provides [API](http://ac6502b637b6641b9bbb6ca95c2df190-1965366291.us-west-1.elb.amazonaws.com:8092/data-jobs/swagger-ui.html#/) for managing the lifecycle of Data Jobs. 

### VDK Plugins 
Versatile Data Kit provides a way to extend or change the behavior of any SDK command using VDK Plugins. 
One can plugin into any stage of the job runtime. For a list of already developed plugins see [plugins directory here](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins). For how to install and develop plugin see [plugin doc](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/README_PLUGINS.md)

### OpId, ExecutionId, AttemptId

![](https://mermaid.ink/img/eyJjb2RlIjoiXG5ncmFwaCBMUlxuICAgIFZES0FnZW50KFZESyBDTEkgb3IgVUkpXG4gICAgVkRLQVBJKFZESyBSRVNUIEFQSSlcbiAgICBFeGVjdXRpb24xKEV4ZWN1dGlvbklkOiAwMSlcbiAgICBFeGVjdXRpb24yKEV4ZWN1dGlvbklkOiAwMilcbiAgICBBdHRlbXB0MTEoRXhlYyAwMSBBdHRlbXB0SWQ6IDAxKVxuICAgIEF0dGVtcHQxMihFeGVjIDAxIEF0dGVtcHRJZDogMDIpXG4gICAgQXR0ZW1wdDIxKEV4ZWMgMDIgQXR0ZW1wdElkOiAwMSlcbiAgICBWREtBZ2VudCAtLT4gfCBPcElkIDAxIHwgVkRLQVBJXG4gICAgVkRLQVBJIC0tPiB8IE9wSWQgMDEgfCBFeGVjdXRpb24xXG4gICAgVkRLQVBJIC0tPiB8IE9wSWQgMDEgfCBFeGVjdXRpb24yXG4gICAgRXhlY3V0aW9uMSAtLT4gfCBPcElkIDAxIHwgQXR0ZW1wdDExXG4gICAgRXhlY3V0aW9uMSAtLT4gfCBPcElkIDAxIHwgQXR0ZW1wdDEyXG4gICAgRXhlY3V0aW9uMiAtLT4gfCBPcElkIDAxIHwgQXR0ZW1wdDIxIiwibWVybWFpZCI6eyJ0aGVtZSI6ImRlZmF1bHQifSwidXBkYXRlRWRpdG9yIjpmYWxzZSwiYXV0b1N5bmMiOnRydWUsInVwZGF0ZURpYWdyYW0iOmZhbHNlfQ)

OpId identifies the trigger that initiated the job operation(s). OpID is similar to trace ID in open tracing. It enable tracing multiple operations across different services and datasets. For example, it is possible to have N jobs with the same OpID (if Job1 started Job2 then Job1.opId = Job2.opId). In HTTP requests it is passed as header 'X-OPID' by the Control Service. In SDK see [OP_ID config option](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/internal/builtin_plugins/config/vdk_config.py#L72)

For ExecutionId - see definition of [Execution](#data-job-execution)<br>
For AttemptId - see definition of [Attempt](#data-job-attempt)

