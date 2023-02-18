## Overview

In this example, we will use a local installation of the Versatile Data Kit Control Service to create and schedule a continuously running [Data Job](https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job). The job itself will merely print a message in the logs.

Before you continue, make sure you are familiar with the [[Getting Started|getting started]] section of the wiki.

## Prerequisites

In order to install the Control Service of the Versatile Data Kit locally, the following products are required:
- [helm](https://helm.sh/docs/intro/install)
- [docker](https://docs.docker.com/get-docker)
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) (version 0.11.1 or later)

## Installation

### Install SDK

You can install Versatile Data Kit and the plugins required for this example by running the following commands from a terminal:
```sh
pip install quickstart-vdk
```
Note that Versatile Data Kit requires Python 3.7+. 
See the [[Installation page|installation#install-sdk]] for more details.

### Install and start the Control Service server

Now you can install the Control Service in a local Kind cluster by running:
```sh
vdk server --install
```
This will install and start up the Versatile Data Kit Control Service.


<details>
<summary><i>For the curious: what is going on behind the scenes?</i></summary>

> This will create a Kind cluster (called "vdk") and deploy the Control Service (with all necessary components) inside this cluster.
<br> This will also create two docker containers locally (called "vdk-docker-registry" and "vdk-git-server" respectively) which are required for the Control Service to work.

</details>


Optionally, you can check the status of the Control Service installation by running:
```sh
vdk server --status
```
This should display the following message if the installation was successful: "The Versatile Data Kit Control Service is installed"

## Data Job

After the Control Service is installed, you can create a new Data Job by running the `vdk create` command:

Run `vdk create --help` to see what are all the options and examples. 

If you run
```sh
vdk create 
```
It will prompt you for all the necessary info. The rest of this example assumes that the selected job name is hello-world.

To verify that the job was indeed created in the Control Service, list all jobs:

```sh
vdk list --all
```
This should produce the following output:
<pre>
job_name     job_team    status
-----------  ----------  ------------
hello-world  my-team     NOT_DEPLOYED
</pre>

You can also observe the code of the newly created Data Job by inspecting the content of the hello-world folder in the current directory. The code will be organized in the following structure:
```
hello-world/
├── 10_python_step.py
├── 20_sql_step.sql
├── config.ini
├── README.md
├── requirements.txt
```

This is a Data Job sample that you can modify in order to customize the Data Job to your needs. For more information on the structure of the Data Jobs, please check the [[Getting Started|getting started]] page.

For the purpose of this example, let's delete the python and sql step and just leave one python step file - 10_python_step.py with the following content:
```python
def run(job_input):
    print(f'\n============ HELLO WORLD! ============\n')
```

Finally, modify the `schedule_cron` property inside the config.ini file as follows:
```ini
schedule_cron = */2 * * * *
```
This property specifies the execution schedule for the Data Job when it is deployed. `*/2 * * * *` indicates that the Data Job will be executed every 2 minutes.

After the changes we have the following file structure:
```
hello-world/
├── 10_python_step.py
├── config.ini
├── README.md
├── requirements.txt
```

## Deployment

Now that we are done with the modifications to the Data Job, we will deploy it in the local Control Service by using the following command:
```sh
vdk deploy -n hello-world -t my-team -p ./hello-world -r "initial commit"
```

This will submit the code of the Data Job to the Control Service and will create a [Data Job Deployment](https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job-deployment). The Deployment process is asynchronous and even though the command completes fast, the creation takes a while until the Data Job is deployed and ready for execution. You can validate that the Data Job Deployment is completed by running the following command:
```sh
vdk deploy --show -n hello-world -t my-team
```

If the deployment is still ongoing, you will get the following output:
```
No deployments.
```

When the deployment completes, the command will print the following:
```
job_name     job_version       last_deployed_by    last_deployed_date           enabled
-----------  ----------------  ------------------  ---------------------------  ---------
hello-world  5000/hello-world                      2021-09-14T12:06:32.999160Z  True
```


<details>
<summary><i>For the curious: what is going on behind the scenes?</i></summary>
<blockquote>
If you have kubectl (https://kubernetes.io/docs/tasks/tools/#kubectl) you can observe the Deployment creation process directly in the Kind cluster. To do this, first get all the pods in the cluster by using:
<pre>
kubectl get pods
</pre>
This will list all pods in the cluster. The one of interest starts with `builder-hello-world` and is dedicated to creating the Data Job image from the Data Job's source code. This image will be subsequently used for the job execution. The builder pod will look like this:
<pre>
NAME                                       READY   STATUS             RESTARTS      AGE
builder-hello-world--1-kcvt9               1/1     Running            0             4s
</pre>
<br>
Once this pod completes, the Control Service will create a [cronjob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) corresponding to the Data Job Deployment. This cronjob is responsible for scheduling the job executions. Listing the cronjobs in the cluster with `kubectl get cronjobs` will show:
<pre>
NAME                 SCHEDULE      SUSPEND   ACTIVE   LAST SCHEDULE   AGE
hello-world-latest   */2 * * * *   False     0        66s             8m33s
</pre>
</blockquote>
</details>

## Execution

After the deployment is complete, the job will be automatically executed by the Control Service as per its schedule. The list of executions can be verified at any point by using the following command:
```sh
vdk execute --list -n hello-world -t my-team
```

This should show details about the last executions of the Data Job:
<pre>
id                           job_name     status    type       start_time                 end_time                   started_by    message         op_id                        job_version
---------------------------  -----------  --------  ---------  -------------------------  -------------------------  ------------  --------------  ---------------------------  ----------------------------------------
hello-world-latest-27193696  hello-world  finished  scheduled  2021-09-14 12:16:00+00:00  2021-09-14 12:16:51+00:00                Success         hello-world-latest-27193696  d9eedb67fc8d52301dbb61c6d9db4397c3f9a9ec
hello-world-latest-27193698  hello-world  finished  scheduled  2021-09-14 12:18:00+00:00  2021-09-14 12:18:57+00:00                Success         hello-world-latest-27193698  d9eedb67fc8d52301dbb61c6d9db4397c3f9a9ec
hello-world-latest-27193700  hello-world  finished  scheduled  2021-09-14 12:20:00+00:00  2021-09-14 12:20:53+00:00                Success         hello-world-latest-27193700  d9eedb67fc8d52301dbb61c6d9db4397c3f9a9ec
hello-world-latest-27193702  hello-world  finished  scheduled  2021-09-14 12:22:00+00:00  2021-09-14 12:22:58+00:00                Success         hello-world-latest-27193702  d9eedb67fc8d52301dbb61c6d9db4397c3f9a9ec
hello-world-latest-27193704  hello-world  running   scheduled  2021-09-14 12:24:00+00:00                                                           hello-world-latest-27193704  d9eedb67fc8d52301dbb61c6d9db4397c3f9a9ec
</pre>

A new execution can be started manually at any time by using the following command:
```sh
vdk execute --start -n hello-world -t my-team
```

This command can potentially fail if there is an already running Data Job execution of the hello-world job at this time because parallel executions of the same job are currently not allowed, in order to ensure data integrity.


<details>
<summary><i>For the curious: what is going on behind the scenes?</i></summary>
<blockquote>

Every execution is carried out by a pod. You can see the execution if you get the list of pods in the cluster:
```sh
kubectl get pods
```

The names of the pods corresponding to our Data Job start with the Data Job name (e.g. hello-world-latest-27193734--1-gb8t2). Find one such pod and show details by running:
```sh
kubectl describe hello-world-latest-27193734--1-gb8t2
```
</blockquote>
</details>

### Check execution logs

Finally, to check the logs of a [Data Job Execution](https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job-execution) use: 
```bash
vdk execute --logs -n hello-world -t my-team --execution-id [execution-id-printed-from-vdk-execute-start]
```

Keep in mind that logs are kept only for the last few executions of a Data Job so looking too far into the past is not possible.