## Overview

In this example, we will use the Versatile Data Kit to develop a [Data Job](https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job)
which [ingests](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L90) data from a REST API to an SQLite database.

Before you continue, ensure you are familiar with the [[Getting Started|getting started]] section of the wiki.

## Code

The relevant Data Job code is available [here](https://github.com/vmware/versatile-data-kit/tree/main/examples/ingest-from-rest-api-example).

You can follow along and run this example Data Job on your machine to get first-hand experience working with Data Jobs; alternatively, you can use the available code as a template and extend it to make a Data Job that fits your use case more closely.

## Database

We will be using a temporary SQLite database, which will be created for us **automatically**.

## Configuration

You can install Versatile Data Kit and the plugins required for this example by running the following commands from a terminal:
```sh
pip install quickstart-vdk
```
Note that Versatile Data Kit requires Python 3.7+.
See the [[Installation page|installation#install-sdk]] for more details.

Ingestion requires us to set the default database type and the ingestion method, or the type of database we will be ingesting to, as environment variables:
```sh
export VDK_DB_DEFAULT_TYPE=SQLITE
export VDK_INGEST_METHOD_DEFAULT=SQLITE
```

**Note:** if you want to ingest data into another target (another database, for example - Postgres, Trino), install the appropriate plugin using `pip install vdk-plugin-name` and change VDK_INGEST_METHOD_DEFAULT. See a list of plugins [here](https://github.com/vmware/versatile-data-kit/wiki/Ingesting-data-from-DB-into-Database) 

To see all possible configuration options, use the command `vdk config-help`

## Data Job

The structure of our Data Job is as follows:

```
ingest-from-rest-api-example-job/
├── 10_delete_table.sql
├── 20_create_table.sql
├── 30_rest_ingest.py
```
Note that the Data Job name is the same as the directory that contains the steps of the job.

The purpose of our Data Job `ingest-from-rest-api-example-job` is to make a GET request to a REST API, and then ingest the returned JSON
to the target database.

Our Data Job consists of two SQL steps and one Python step. Note that VDK enables us to combine Python and SQL steps in any preferred order.
Since steps are executed in alphabetical order, it is a good practice to prefix the step titles with numbers. This makes the sequence of the steps clear to Versatile Data Kit and other users who may browse through the Data Job.

<details>
<summary>10_delete_table.sql</summary>
<pre>
DROP TABLE IF EXISTS rest_target_table;
</pre>
</details>

<details>
<summary>20_create_table.sql</summary>
<pre>
CREATE TABLE rest_target_table (userId, id, title, completed);
</pre>
</details>

<details>
<summary>30_rest_ingest.py</summary>
<pre>
import requests

def run(job_input):
    response = requests.get("https://jsonplaceholder.typicode.com/todos/1")
    response.raise_for_status()
    payload = response.json()
    job_input.send_object_for_ingestion(
        payload=payload,
        destination_table="rest_target_table"
    )
</pre>
</details>

- The first step deletes the new table if it exists. This query only serves to make the Data Job repeatable;
- The second step creates the table that will be used to store the data;
- The third step requests the payload from the specified REST API and ingests it into the destination_table in the target database.
<details>
<summary>Sample json</summary>
<pre>
{
userId: 1,
id: 1,
title: "delectus aut autem",
completed: false
}
</pre>
</details>

To run the Data Job, we navigate to the parent directory of the Job and run the following command from a terminal:
```sh
vdk run ingest-from-rest-api-example-job/
```
Upon successful completion of the Data Job, we should see a log similar to this:
<details>
<summary>Result logs</summary>
<pre>
2021-08-27 15:04:35,381=1630065875[VDK] ingest-from-rest-api-example-job [INFO ] vdk.internal.builtin_plugins.run           cli_run.py:66   run_job         [OpId:1630065872-e39532-3f42e6]- Data Job execution summary: {
  "data_job_name": "ingest-from-rest-api-example-job",
  "execution_id": "1630065872-e39532",
  "start_time": "2021-08-27T12:04:33.186862",
  "end_time": "2021-08-27T12:04:33.354630",
  "status": "success",
  "steps_list": [
    {
      "name": "10_delete_table.sql",
      "type": "sql",
      "start_time": "2021-08-27T12:04:33.186885",
      "end_time": "2021-08-27T12:04:33.194096",
      "status": "success",
      "details": null,
      "exception": null
    },
    {
      "name": "20_create_table.sql",
      "type": "sql",
      "start_time": "2021-08-27T12:04:33.194160",
      "end_time": "2021-08-27T12:04:33.196529",
      "status": "success",
      "details": null,
      "exception": null
    },
    {
      "name": "30_rest_ingest.py",
      "type": "python",
      "start_time": "2021-08-27T12:04:33.196575",
      "end_time": "2021-08-27T12:04:33.354595",
      "status": "success",
      "details": null,
      "exception": null
    }
  ],
  "exception": null
}
</pre>
</details>

After running the Data Job, we can check whether the new table was populated correctly by using the `sqlite-query` command afforded to us by the `vdk-sqlite` plugin, which we can use to execute queries against the configured SQLite database without having to set up a Data Job:
```
vdk sqlite-query -q 'SELECT * FROM rest_target_table'
```

We should see the following output:
```
-  -  ------------------  -
1  1  delectus aut autem  0
-  -  ------------------  -
```

## What's next

You can find a list of all Versatile Data Kit examples [here](https://github.com/vmware/versatile-data-kit/wiki/Examples).
