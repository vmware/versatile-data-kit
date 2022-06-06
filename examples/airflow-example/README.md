Overview
--------

In this example we will use the Versatile Data Kit to develop three Datajobs which will be managed through an Airflow DAG. Two of these jobs will ingest data from separate sources, and the third job will aggregate the ingested data into a new table.

Before you continue, make sure you are familiar with the [Getting Started](https://github.com/vmware/versatile-data-kit/wiki/Getting-Started) section of the wiki.

Code
----

The relevant Data Job and Airflow DAG code is available [here]().

You can follow along and run this example DAG on your machine; alternatively, you can use the available code as a template and extend it to make a DAG that fits your use case more closely.

Database
--------


Configuration
-------------
You must install Airflow and the VDK provider for Airflow. You can find the Airflow Quick-Start guide [here](https://airflow.apache.org/docs/apache-airflow/stable/start/local.html).
You can install the airflow-provider-vdk package using the following command:
```console
pip install airflow-provider-vdk
```

If you have not done so already, you can install Versatile Data Kit and the plugins required for this example by running the following commands from a terminal:
```console
pip install quickstart-vdk
```
Note that Versatile Data Kit requires Python 3.7+. See the [Installation page](https://github.com/vmware/versatile-data-kit/wiki/Installation#install-sdk) for more details.



Please note that this example requires deploying Datajobs in a Kubernetes environment, which means that you would also need to install the **VDK Control Service.**

<ins>Prerequisites</ins>:

*   Install [helm](https://helm.sh/docs/intro/install)
*   Install [docker](https://docs.docker.com/get-docker)
*   Install [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) (version 0.11.1 or later)

<ins>Then run</ins>:
```console
vdk server --install
```

This example requires us to set environment variables for:

1.  the default database type that we will be ingesting data from;
2.  the ingestion method;
3.  the location of the target database - if this file is not present, VDK will create it automatically. For this example, we will use `vdk-airflow-example.db` as our database which will be created in the current directory;
4.  the URL for the VDK control service API.

Enter the following commands in the command prompt (if you are on a Windows system, use `set` keyword instead of `export`):
```console
export VDK_DB_DEFAULT_TYPE=SQLITE
export VDK_INGEST_METHOD_DEFAULT=sqlite
export VDK_INGEST_TARGET_DEFAULT=vdk-increment-sqlite.db
export VDK_CONTROL_SERVICE_REST_API_URL=http://localhost:8092/
```
**Note:** If you want to ingest data into another target (i.e. another database - Postgres, Trino, etc.), install the appropriate plugin using `pip install vdk-plugin-name` and change `VDK_INGEST_METHOD_DEFAULT` environment variable. See a list of plugins [here](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins).

To see all possible configuration options, use the command `vdk config-help.`

Additionally, you will need to configure the Airflow connection to the VDK control-service using the following command:
```console
airflow connection add
```

Data Jobs
--------

Our three Datajobs have the following structure:

```
airflow-ingest-job1/
├── 10_ingest.py
├── config.ini
```

```
airflow-ingest-job2/
├── 10_ingest.py
├── config.ini
```

```
airflow-transform-job/
├── 10_transform.py
├── config.ini
```

<details>
  <summary>10_ingest.py</summary>

```py

```
</details>


Execution
---------



What's next
-----------

You can find a list of all Versatile Data Kit examples [here](https://github.com/vmware/versatile-data-kit/wiki/Examples).
