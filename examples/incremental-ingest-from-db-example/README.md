Overview
--------

In this example we will use the Versatile Data Kit to develop an incremental [ingestion](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L90) [Data Job](https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job). This job will read data from one local SQLite database and write into another local SQLite database only the records that are not present in the target table, thus enriching the target.

Before you continue, make sure you are familiar with the [Getting Started](https://github.com/vmware/versatile-data-kit/wiki/Getting-Started) section of the wiki.

Code
----

The relevant Data Job code is available [here](https://github.com/vmware/versatile-data-kit/tree/main/examples).

You can follow along and run this example Data Job on your machine to get first-hand experience working with Data Jobs; alternatively, you can use the available code as a template and extend it to make a Data Job that fits your use case more closely.

Database
--------

We will be using a local SQLite database that was built for the purposes of the example. The initial version of this database can be found in the data job repository, subfolder "data_for_initial_run".

The contents of the uploaded data source are the following (**`incremental_ingest_example.db`** → table **`increm_ingest`**):

| id | descr | reported_date |
| --- | --- | --- |
| 1 | record one | 10-01-2021 |
| 2 | second record | 10-02-2021 |
| 3 | this is record 3 | 10-03-2021 |

After the initial ingestion takes place (the data job is run once, the target table is created and populated with the 3 records illustrated in the table above), the source table `increm_ingest` in the `incremental_ingest_example.db` database needs to be enriched with a few more records in order to illustrate how those new records will be incrementally ingested into the target database.

The following records are added:

| id | descr | reported_date |
| --- | --- | --- |
| 4 | that's a new record! | 11-01-2021 |
| 5 | and another new record.. | 11-02-2021 |

The enriched data source could be downloaded from the data job repository, subfolder "data_for_subsequent_run".

Configuration
-------------

If you have not done so already, you can install Versatile Data Kit and the plugins required for this example by running the following commands from a terminal:
```console
pip install quickstart-vdk
```
Note that Versatile Data Kit requires Python 3.7+. See the [Installation page](https://github.com/vmware/versatile-data-kit/wiki/Installation#install-sdk) for more details.



Please note that this example uses data job properties, which means that you would also need to install **VDK Control Service.**

<ins>Prerequisites</ins>:

*   Install [helm](https://helm.sh/docs/intro/install)
*   Install [docker](https://docs.docker.com/get-docker)
*   Install [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) (version 0.11.1 or later)

<ins>Then run</ins>:
```console
vdk server --install
```

Ingestion requires us to set environment variables for:

1.  the type of database in which we will be ingesting;
2.  the ingestion method;
3.  the ingestion target - the location of the target database - if this file is not present, ingestion will create it in the current directory. For this example, we will use `vdk-increment-sqlite.db` file which will be created in the current directory;
4.  the file of the default SQLite database against which vdk runs - initially we set this to the origin SQLite DB since we will be querying it first, and later we can change it to the target to check the results from ingestion;
5.  the URL for the VDK control service API (in case of using job properties).

Enter the following commands in the command prompt (if you are on a Windows system, use `set` keyword instead of `export`):
```console
export VDK_DB_DEFAULT_TYPE=SQLITE
export VDK_INGEST_METHOD_DEFAULT=sqlite
export VDK_INGEST_TARGET_DEFAULT=vdk-increment-sqlite.db
export VDK_SQLITE_FILE=VDK_SQLITE_FILE=<path_to_datajob_folder>\data\incremental_ingest_example.db
export VDK_CONTROL_SERVICE_REST_API_URL=http://localhost:8092/
```
**Note:** If you want to ingest data into another target (i.e. another database - Postgres, Trino, etc.), install the appropriate plugin using `pip install vdk-plugin-name` and change `VDK_INGEST_METHOD_DEFAULT` environment variable. See a list of plugins [here](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins).

To see all possible configuration options, use the command `vdk config-help.`

**Instead of using environment variables, the alternative option is to set these configuration parameters in the config.ini file of the data job under the [vdk] section.**

Data Job
--------

The structure of our Data Job is as follows:

```
incremental-ingest-from-db-example/
├── data_for_initial_run/
├──── incremental_ingest_example.db
├── data_for_subsequent_run/
├──── incremental_ingest_example.db
├── 10_increm_ingest_from_db_example.py
├── README.md
```

The purpose of this example is to demonstrate how the user can query data from a source database and then ingest it to the target database in an incremental fashion (only enriching the target with any new data added to the source). Our Data Job `incremental-ingest-from-db-example` uses local SQLite database as source (`incremental_ingest_example.db`) and local SQLite database as target (`vdk-increment-sqlite.db`) where we create the backup table of the source.

`incremental-ingest-from-db-example` consists of only one Python step. In general, VDK allows us to mix Python and SQL steps in whatever order we would prefer. The reason the step names are prefixed by numbers is that steps are executed in alphabetical order, so it is a good practice to prefix them thus making their order clear both to Versatile Data Kit and to other users who might read through the Data Job.

<details>
  <summary>10_increm_ingest_from_db_example.py</summary>

```py
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):

    # Get last_date property/parameter:
    #  - if the this is the first job run, initialize last_date to 01-01-1900 in oder to fetch all rows
    #  - if the data job was run previously, take the property value already stored in the DJ from the previous run
    last_date = job_input.get_property("last_date", "01-01-1900")

    # Select the needed records from the source table using job_input's built-in method and a query parameter
    data = job_input.execute_query(
        f"""
        SELECT * FROM increm_ingest
        WHERE reported_date > '{last_date}'
        ORDER BY reported_date
        """
    )
    # Fetch table info containing the column names
    table_info = job_input.execute_query("PRAGMA table_info(increm_ingest)")

    # If any data is returned from the query, send the fetched records for ingestion
    if len(data) > 0:
        job_input.send_tabular_data_for_ingestion(
            data,
            column_names=[column[1] for column in table_info],
            destination_table="incremental_ingest_from_db_example",
        )

        # Reset the last_date property value to the latest date in the source db table
        job_input.set_all_properties({"last_date": max(row[2] for row in data)})

    print(f"Success! {len(data)} rows were inserted.")
```
</details>

The code fetches the necessary records from the source SQLite DB and writes them into the `incremental_ingest_from_db_example` table in the target `vdk-increment-sqlite` database. This is done using the built-in methods of VDK's job_input interface `job_input.execute_query()` and `job_input.send_tabular_data_for_ingestion()`.

To determine whether to ingest all records from the source or only the once that are not present in the target already, the `last_date` job property is used. Job properties allow storing state and/or credentials; there are pre-defined methods of the job_input interface that can be directly adopted by users of VDK. The documentation on data job properties' methods can be found [here](https://github.com/vmware/versatile-data-kit/blob/246008c8fffcac173b6ac3f434814acb6faf16a7/projects/vdk-core/src/vdk/api/job_input.py#L11).

Execution
---------

To run the Data Job, we navigate to the parent directory of the Job and run the following command from a terminal:

```console
vdk run incremental-ingest-from-db-example-job
```

**NB: If your current directory is not the parent directory of the Job, some command and path tweaks might be needed for the Job to complete successfully.**

Upon successful completion of the Data Job, we should see a log similar to this:

<details>
  <summary>Result log</summary>

```console
2021-12-13 15:54:07,047=1639403647[VDK] incremental-ingest-from-db-example [INFO ] vdk.internal.builtin_plugins.r           cli_run.py:66   run_job         [OpId:26b1a9e4-4b93-4f96-a223-f2bb210256e5-1639403644-376e6]- Data Job execution summary: {
  "data_job_name": "incremental-ingest-from-db-example",
  "execution_id": "26b1a9e4-4b93-4f96-a223-f2bb210256e5-1639403644",
  "start_time": "2021-12-13T13:54:04.462304",
  "end_time": "2021-12-13T13:54:05.030316",
  "status": "success",
  "steps_list": [
    {
      "name": "10_increm_ingest_from_db_example.py",
      "type": "python",
      "start_time": "2021-12-13T13:54:04.462304",
      "end_time": "2021-12-13T13:54:05.030316",
      "status": "success",
      "details": null,
      "exception": null
    }
  ],
  "exception": null
}
```
</details>

**Please remember to download the enriched source DB** after running the data job for the first time (as explained in the Database section above) in case you want to track the incremental ingestion effect. If the data job is run again with the initial source, no new data will be ingested and the target table will stay the same.

After running the data job, we can check whether the new backup table was populated correctly by using the `sqlite-query` command afforded to us by the `vdk-sqlite` plugin, which we can use to execute queries against the configured SQLite database (`VDK_SQLITE_FILE` environment variable) without having to set up a data job for that.
Since initially the `VDK_SQLITE_FILE` environment variable was set to the source DB, we need to reassign it to query the target DB instead and then execute the `sqlite-query` command:

```
export/set VDK_SQLITE_FILE=vdk-increment-sqlite.db
vdk sqlite-query -q "SELECT * FROM incremental_ingest_from_db_example"
```

After the initial ingestion, we should see the following output:

```
---------------------------------------------------------------------------------------------
Creating new connection against local file database located at: vdk-increment-sqlite.db

id   descr               reported_date
--------------------------------------
1    record one          10-01-2021
2    second record       10-02-2021
3    this is record 3    10-03-2021
---------------------------------------------------------------------------------------------
```

After the incremental ingestion, we should see the 2 new records appended at the end of the table:

```
---------------------------------------------------------------------------------------------
Creating new connection against local file database located at: vdk-increment-sqlite.db

id    descr                       reported_date
----------------------------------------------
1     record one                  10-01-2021
2     second record               10-02-2021
3     this is record 3            10-03-2021
4     that's a new record!        11-01-2021
5     and another new record..    11-02-2021
---------------------------------------------------------------------------------------------
```

What's next
-----------

You can find a list of all Versatile Data Kit examples [here](https://github.com/vmware/versatile-data-kit/wiki/Examples).
