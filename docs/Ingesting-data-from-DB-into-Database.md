## Overview

In this example we will use the Versatile Data Kit to develop an [ingestion](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L90)
[Data Job](https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job).
This job will read data from one local SQLite database and write it into another local SQLite database, thus creating a backup for a table.

Before you continue, make sure you are familiar with the [[Getting Started|getting started]] section of the wiki.

## Code

The relevant Data Job code is available [here](https://github.com/vmware/versatile-data-kit/tree/main/examples/ingest-from-db-example).

You can follow along and run this example Data Job on your machine to get first-hand experience working with Data Jobs; alternatively, you can use the available code as a template and extend it to make a Data Job that fits your use case more closely.

## Database

We will be using the chinook SQLite database. It is available [here](https://www.sqlitetutorial.net/sqlite-sample-database/). Users of Unix-based operating systems can download it using the following commands, provided you have the `curl` and `unzip` tools installed:
```sh
curl https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip >> chinook.zip
unzip chinook.zip
rm -r chinook.zip
```
You should now find a `chinook.db` file in the same directory that you downloaded the original zip file in.

Alternatively, Windows users can download the zip file through the provided link, and extract it in a convenient location.

**NB: After downloading and extracting the `chinook.db` file, place it in your local directory (the Data Job parent directory), as otherwise the sqlite3 module will create a new file named `chinook.db` and display an error stating that it cannot find the necessary table in it.**

## Configuration

If you have not done so already, you can install Versatile Data Kit and the plugins required for this example by running the following commands from a terminal:
```sh
pip install quickstart-vdk
```
Note that Versatile Data Kit requires Python 3.7+. 
See the [[Installation page|installation#install-sdk]] for more details.

Ingestion requires us to set environment variables for:
- the type of database in which we will be ingesting;
- the ingestion method;
- the ingestion target - the location of the target database - if this file is not present, ingestion will create it in the current directory. For this example, we will use vdk-sqlite.db file which will be created in the current directory;
- the file of the default SQLite database against which vdk runs (same value as ingestion target in this case);

```sh
export VDK_DB_DEFAULT_TYPE=SQLITE
export VDK_INGEST_METHOD_DEFAULT=sqlite
export VDK_INGEST_TARGET_DEFAULT=vdk-sqlite.db
export VDK_SQLITE_FILE=vdk-sqlite.db
```

**Note:** if you want to ingest data into another target (another database for example - Postgres, Trino), install the appropriate plugin using `pip install vdk-plugin-name` and change VDK_INGEST_METHOD_DEFAULT. See a list of plugins [here](https://github.com/vmware/versatile-data-kit/wiki/Ingesting-data-from-DB-into-Database) 

To see all possible configuration options use command `vdk config-help`

## Data Job

The structure of our Data Job is as follows:

```
ingest-from-db-example-job/
├── 10_drop_table.sql
├── 20_create_table.sql
├── 30_ingest_to_table.py
```

The purpose of this example is to demonstrate how the user can query data from a source database and then ingest it to the
target database. Our Data Job `ingest-from-db-example-job` uses local chinook.db SQLite database as source and local vdk-sqlite.db SQLite database as target where we
create the backup table of the chinook employees table.

`ingest-from-db-example-job` consists of two SQL steps and one Python step. Note that VDK allows us the mix Python and SQL steps in whatever order we would prefer.
The reason the step names are prefixed by numbers is that steps are executed in alphabetical order, so it is a good practice to prefix the steps with numbers, which makes their order clear both to Versatile Data Kit and to other users who might read through the Data Job.

<details>
<summary>10_drop_table.sql</summary>
<pre>
DROP TABLE IF EXISTS backup_employees;
</pre>
</details>

<details>
<summary>20_create_table.sql</summary>
<pre>
CREATE TABLE backup_employees (
    EmployeeId INTEGER,
    LastName   NVARCHAR,
    FirstName  NVARCHAR,
    Title      NVARCHAR,
    ReportsTo  INTEGER,
    BirthDate  NVARCHAR,
    HireDate   NVARCHAR,
    Address    NVARCHAR,
    City       NVARCHAR,
    State      NVARCHAR,
    Country    NVARCHAR,
    PostalCode NVARCHAR,
    Phone      NVARCHAR,
    Fax        NVARCHAR,
    Email      NVARCHAR
);
</pre>
</details>

<details>
<summary>30_ingest_to_table.py</summary>
<pre>
import sqlite3<br><br>
def run(job_input):
    db_connection = sqlite3.connect(
        "chinook.db"
    )  # if chinook.db file is not in your current directory, replace "chinook.db" with the path to your chinook.db file
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM employees")
    job_input.send_tabular_data_for_ingestion(
        cursor,
        column_names=[column_info[0] for column_info in cursor.description],
        destination_table="backup_employees",
    )
</pre>
</details>

- The first step deletes the backup table if it exists. This query only serves to make the Data Job repeatable;
- The second step creates the backup table we will be inserting data into;
- The third step makes a connection to the source database, queries data from it, and then ingests the returned data into the destination_table in the target database.

To run the Data Job, we navigate to the parent directory of the Job, and run the following command from a terminal:
```sh
vdk run ingest-from-db-example-job/
```

**NB: If your current directory is not the parent directory of the Job, some command and path tweaks might be needed for the Job to complete successfully.**

Upon successful completion of the Data Job, we should see a log similar to this:
<details>
<summary>Result logs</summary>
<pre>
2021-09-01 13:31:00,021=1630492260[VDK] ingest-from-db-example-job [INFO ] vdk.internal.builtin_plugins.run           cli_run.py:66   run_job         [OpId:1630492257-154210-b68194]- Data Job execution summary: {
  "data_job_name": "ingest-from-db-example-job",
  "execution_id": "1630492257-154210",
  "start_time": "2021-09-01T10:30:57.934062",
  "end_time": "2021-09-01T10:30:57.959046",
  "status": "success",
  "steps_list": [
    {
      "name": "10_drop_table.sql",
      "type": "sql",
      "start_time": "2021-09-01T10:30:57.934125",
      "end_time": "2021-09-01T10:30:57.941691",
      "status": "success",
      "details": null,
      "exception": null
    },
    {
      "name": "20_create_table.sql",
      "type": "sql",
      "start_time": "2021-09-01T10:30:57.941803",
      "end_time": "2021-09-01T10:30:57.946523",
      "status": "success",
      "details": null,
      "exception": null
    },
    {
      "name": "30_ingest_to_table.py",
      "type": "python",
      "start_time": "2021-09-01T10:30:57.946630",
      "end_time": "2021-09-01T10:30:57.958948",
      "status": "success",
      "details": null,
      "exception": null
    }
  ],
  "exception": null
}
</pre>
</details>

After running the Data Job, we can check whether the new backup table was populated correctly by using the `sqlite-query` command afforded to us by the `vdk-sqlite` plugin,
which we can use to execute queries against the configured SQLite database (VDK_SQLITE_FILE environment variable) without having to set up a Data Job:
```
vdk sqlite-query -q 'SELECT * FROM backup_employees'
```

We should see the following output:
```
-  --------  --------  -------------------  -  -------------------  -------------------  ---------------------------  ----------  --  ------  -------  -----------------  -----------------  ------------------------
1  Adams     Andrew    General Manager         1962-02-18 00:00:00  2002-08-14 00:00:00  11120 Jasper Ave NW          Edmonton    AB  Canada  T5K 2N1  +1 (780) 428-9482  +1 (780) 428-3457  andrew@chinookcorp.com
2  Edwards   Nancy     Sales Manager        1  1958-12-08 00:00:00  2002-05-01 00:00:00  825 8 Ave SW                 Calgary     AB  Canada  T2P 2T3  +1 (403) 262-3443  +1 (403) 262-3322  nancy@chinookcorp.com
3  Peacock   Jane      Sales Support Agent  2  1973-08-29 00:00:00  2002-04-01 00:00:00  1111 6 Ave SW                Calgary     AB  Canada  T2P 5M5  +1 (403) 262-3443  +1 (403) 262-6712  jane@chinookcorp.com
4  Park      Margaret  Sales Support Agent  2  1947-09-19 00:00:00  2003-05-03 00:00:00  683 10 Street SW             Calgary     AB  Canada  T2P 5G3  +1 (403) 263-4423  +1 (403) 263-4289  margaret@chinookcorp.com
5  Johnson   Steve     Sales Support Agent  2  1965-03-03 00:00:00  2003-10-17 00:00:00  7727B 41 Ave                 Calgary     AB  Canada  T3B 1Y7  1 (780) 836-9987   1 (780) 836-9543   steve@chinookcorp.com
6  Mitchell  Michael   IT Manager           1  1973-07-01 00:00:00  2003-10-17 00:00:00  5827 Bowness Road NW         Calgary     AB  Canada  T3B 0C5  +1 (403) 246-9887  +1 (403) 246-9899  michael@chinookcorp.com
7  King      Robert    IT Staff             6  1970-05-29 00:00:00  2004-01-02 00:00:00  590 Columbia Boulevard West  Lethbridge  AB  Canada  T1K 5N8  +1 (403) 456-9986  +1 (403) 456-8485  robert@chinookcorp.com
8  Callahan  Laura     IT Staff             6  1968-01-09 00:00:00  2004-03-04 00:00:00  923 7 ST NW                  Lethbridge  AB  Canada  T1H 1Y8  +1 (403) 467-3351  +1 (403) 467-8772  laura@chinookcorp.com
-  --------  --------  -------------------  -  -------------------  -------------------  ---------------------------  ----------  --  ------  -------  -----------------  -----------------  ------------------------
```

## What's next

You can find a list of all Versatile Data Kit examples [here](https://github.com/vmware/versatile-data-kit/wiki/Examples).
