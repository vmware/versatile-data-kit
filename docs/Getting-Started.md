
VDK helps you develop, test, and debug [[Data Jobs|dictionary#data-job]] on your local PC/laptop.

The purpose of this page is to go over the anatomy of a Data Job and walk you through a simple Hello World example.


## Install VDK

```bash
pip install quickstart-vdk
```
Note that Versatile Data Kit requires Python 3.7+.

See the [[Installation page|installation#install-sdk]] for more details.


## Familiarize with vdk 

VDK has very good help. See the list of all commands with: 
```bash
vdk --help
```

Or details on each command with
```bash
vdk [command-name] --help 
```

## Develop your first Data Job
In this section, we will run a simple [[Data Job|dictionary#data-job]] with [[VDK|dictionary#vdk]], and then we'll see the results of the run.

### Create Data Job

```
vdk create -n hello-world -t my-team
```
This will create a data job locally. See `vdk create --help` for details on what each argument does.

If you have Control Service installed, it will also register/create it in the cloud. But let's leave this part for [later](https://github.com/vmware/versatile-data-kit/wiki/Scheduling-a-Data-Job-for-automatic-execution).

You will see that the Data Job was created with some sample files with instructions. 
Feel free to browse the sample files to learn more.

### Data Job files

> _Data Job directory can contain any files, however, some files are treated in a specific way:_
> 
> * **SQL files (.sql)** - called SQL steps - are directly executed as queries against a database.
> * **Python files (.py)** - called Python steps - are python scripts that define a run function that takes as an argument the job_input object.
> * **config.ini** is needed to schedule a job.
> * **requirements.txt** is needed when your Python steps use external python libraries.
 
### Edit Data Job

Now we will change the data job to print "hello world" only. 
The new file structure will be like this: 

```
hello-world/
├── 10_hello_world.py
```

The name of the Data Job is defined by the name of the directory. In this case, we have named the Data Job: hello-world

10_hello_world.py is a python step that will print "HELLO WORLD" to the console.

### Data Job Source 

> _Why is the name of this Python step prefixed with 10?_
> 
> VDK supports having many Python and/or SQL steps in a single Data Job. Steps are executed in ascending alphabetical order based on file names.<br>
> Prefixing file names with numbers makes it easy to have meaningful names while maintaining steps execution order.

Delete the sample files created by the previous step and create a single file, 10_hello_world.py, with the following content: 
```python
def run(job_input):
    print("\n", "HELLO WORLD", "\n")
```

A function named `run` is required for a python script to be recognized as a Data Job Python step.

VDK provides an object to every python step - job_input - that has methods for:

- executing queries against a database;
- ingesting data into a database;
- processing data into a database.
- **See the [job_input](https://github.com/vmware/versatile-data-kit/blob/977b8f903bdd530a634c2cdb7f2e0200eb9e5756/projects/vdk-core/src/vdk/api/job_input.py) documentation for more details.**

### Run Data Job Locally

1. Make sure you have created the Data Job directory and that it contains the Python step from above. 
   
2. Run the Data Job from a Terminal.

```bash
vdk run <path to Data Job directory>
```

3. Upon successful execution of a Data Job, you will see these logs in the console:

<details>
<summary><i>Hello World Job logs</i></summary>
<pre>
Data Jobs Development Kit (VDK)
Version: 0.0.10
Build details: RELEASE_VERSION=0.0.10, BUILD_DATE=Fri Jul 16 16:18:31 UTC 2021, BUILD_MACHINE_INFO=Darwin aivanov-a01.vmware.com 19.6.0 Darwin Kernel Version 19.6.0: Mon Apr 12 20:57:45 PDT 2021; root:xnu-6153.141.28.1~1/RELEASE_X86_64 x86_64, GITLAB_CI_JOB_ID=, GIT_COMMIT_SHA=2a09fe5ec47474ff59e8f6b575758756d90a2cb9, GIT_BRANCH=person/aivanov/current
Installed plugins:
vdk-control-service-properties (from package vdk-plugin-control-cli, version 0.1.2)
vdk-plugin-control-cli (from package vdk-plugin-control-cli, version 0.1.2)
vdk-trino (from package vdk-trino, version 0.1.3)
--------------------------------------------------------------------------------
Run job with directory versatile-data-kit/examples/hello/hello-world

2021-07-25 16:36:57,306=1627220217[VDK] hello-world [DEBUG] vdk.internal.builtin_plugins.con        log_config.py:152  initialize_job  [OpId:1627220217-19b6bb-5b0632]- Initialized logging for log type LOCAL.
2021-07-25 16:36:57,306=1627220217[VDK] hello-world [INFO ] vdk.internal.properties_plugin   properties_plugin.py:99   initialize_job  [OpId:1627220217-19b6bb-5b0632]- Properties API is configured without authentication
2021-07-25 16:36:57,306=1627220217[VDK] hello-world [WARNI] vdk.internal.properties_plugin   properties_plugin.py:108  initialize_job  [OpId:1627220217-19b6bb-5b0632]- Plugin control service properties is installed but required configuration (PROPERTIES_API_URL) is not passed.Control Service based properties will not be setup.
2021-07-25 16:36:57,306=1627220217[VDK] hello-world [DEBUG] vdk.internal.builtin_plugins.run          data_job.py:66   run_step        [OpId:1627220217-19b6bb-5b0632]- Processing step 10_hello_world.py ...
2021-07-25 16:36:57,308=1627220217[VDK] hello-world [INFO ] vdk.internal.builtin_plugins.run   file_based_step.py:80   run_python_step [OpId:1627220217-19b6bb-5b0632]- Entering 10_hello_world.py#run(...) ...

HELLO WORLD

2021-07-25 16:36:57,308=1627220217[VDK] hello-world [INFO ] vdk.internal.builtin_plugins.run   file_based_step.py:86   run_python_step [OpId:1627220217-19b6bb-5b0632]- Exiting  10_hello_world.py#run(...) SUCCESS
2021-07-25 16:36:57,308=1627220217[VDK] hello-world [DEBUG] vdk.internal.builtin_plugins.run          data_job.py:68   run_step        [OpId:1627220217-19b6bb-5b0632]- Processing step 10_hello_world.py completed successfully
2021-07-25 16:36:57,308=1627220217[VDK] hello-world [INFO ] vdk.internalbuiltin_plugins.run           cli_run.py:65   run_job         [OpId:1627220217-19b6bb-5b0632]- Data Job execution summary: {
"data_job_name": "hello-world",
"execution_id": "1627220217-19b6bb",
"start_time": "2021-07-25T13:36:57.306486",
"end_time": "2021-07-25T13:36:57.308373",
"status": "success",
"steps_list": [
{
"name": "10_hello_world.py",
"type": "python",
"start_time": "2021-07-25T13:36:57.306514",
"end_time": "2021-07-25T13:36:57.308346",
"status": "success",
"details": null,
"exception": null
}
],
"exception": null
}

</pre>
</details>

### What's next? 

You have created your first data job. You now know what a data job is. What is the structure of a data job, and how to run a data job.

Now you can jump on more interesting examples like 
* [Ingest data into a local database using REST API](https://github.com/vmware/versatile-data-kit/wiki/Ingesting-data-from-REST-API-into-Database)
* [Process data using SQL and local database](https://github.com/vmware/versatile-data-kit/wiki/Processing-data-using-SQL-and-local-database)

Find a list of all Versatile Data Kit examples [here](https://github.com/vmware/versatile-data-kit/wiki/Examples).