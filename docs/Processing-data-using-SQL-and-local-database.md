## Overview

In this example we will use the Versatile Data Kit to develop a processing [Data Job](https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job). This job will read data from a local SQLite database, process it, and write the result to the same database.

Before you continue, ensure you are familiar with the [[Getting Started|getting started]] section of the wiki.

## Code

The relevant Data Job code is available [here](https://github.com/vmware/versatile-data-kit/tree/main/examples/sqlite-processing-example).

You can follow along and run this example Data Job on your machine to get first-hand experience working with Data Jobs. Alternatively, you can use the available code as a template and extend it to make a Data Job that fits your use case more closely.

## Database

We will be using the chinook SQLite database. It is available [here](https://www.sqlitetutorial.net/sqlite-sample-database/). Users of Unix-based operating systems can download it using the following commands, provided you have the `curl` and `unzip` tools installed:
```sh
curl https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip >> chinook.zip
unzip chinook.zip
rm -r chinook.zip
```
'chinook.db' should now be located in the same directory where the original zip file was downloaded.

Alternatively, Windows users can download the zip file through the provided link and extract it in a convenient location.

**NB: Place the "chinook.db" file in your local directory (the Data Job parent directory) after downloading and extracting it. If you don't, the sqlite3 module will generate a new file with the same name and display an error message saying that it cannot find the required table.**

## Configuration

You can install Versatile Data Kit and the plugins required for this example by running the following commands from a terminal:
```sh
pip install quickstart-vdk
```
Note that Versatile Data Kit requires Python 3.7+.
See the [[Installation page|installation#install-sdk]] for more details.

Your instance of Versatile Data Kit is pre-configured to connect to an SQLite database. The path to the database we just downloaded must be declared as an environment variable.
```sh
export VDK_SQLITE_FILE=chinook.db
```

## Data Job

The structure of our Data Job is as follows:

```
sqlite-example-job/
├── 10_drop_table.sql
├── 20_create_table.sql
├── 30_do_processing.sql
```
Note that the Data Job name is the same as the directory that contains the steps of the job.

The purpose of our Data Job `sqlite-example-job` is to extract the EmployeeId and names of employees who work with customers, and the number of customers they work with, and insert them into a newly-created table called `customer_count_per_employee`.

Our Data Job consists of three SQL steps. Since steps are executed in alphabetical order, it is a good practice to prefix the step titles with numbers. This makes the sequence of the steps clear to the Versatile Data Kit and other users who may browse through the Data Job.


Click on each filename to expand the contents of the file.
<details>
<summary>10_drop_table.sql</summary>
<pre>
DROP TABLE IF EXISTS customer_count_per_employee;
</pre>
</details>

<details>
<summary>20_create_table.sql</summary>
<pre>
CREATE TABLE customer_count_per_employee (EmployeeId, EmployeeFirstName, EmployeeLastName, CustomerCount);
</pre>
</details>

<details>
<summary>30_do_processing.sql</summary>
<pre>
INSERT INTO customer_count_per_employee
SELECT SupportRepId, employees.FirstName, employees.LastName, COUNT(CustomerId)
FROM (customers INNER JOIN employees ON customers.SupportRepId = employees.EmployeeId)
GROUP BY SupportRepId;
</pre>
</details>

Each SQL step is a separate query:
- The first step deletes the new table if it exists. This query only serves to make the Data Job repeatable;
- The second step creates the table we will be inserting data;
- The third step performs the described processing and inserts the new data into the `customer_count_per_employee` table.

All three files must be located in the same `/sqlite-example-job/` directory.

To run the Data Job, we navigate to the parent directory of the Job, and run the following command from a terminal:
```sh
vdk run sqlite-example-job/
```

**NB: If your current directory is not the parent directory of the Job, some command and path tweaks might be needed for the Job to complete successfully.**

Upon successful completion of the Data Job, we should see a log similar to this:
<details>
<summary>Result logs</summary>
<pre>
2021-08-30 09:34:42,143=1630305282[VDK] sqlite-example-job [INFO ] vdk.internal.builtin_plugins.run           cli_run.py:66   run_job         [OpId:1630305281-1bffad-30ea28]- Data Job execution summary: {
  "data_job_name": "sqlite-example-job",
  "execution_id": "1630305281-1bffad",
  "start_time": "2021-08-30T06:34:42.131133",
  "end_time": "2021-08-30T06:34:42.142670",
  "status": "success",
  "steps_list": [
    {
      "name": "10_drop_table.sql",
      "type": "sql",
      "start_time": "2021-08-30T06:34:42.131158",
      "end_time": "2021-08-30T06:34:42.138567",
      "status": "success",
      "details": null,
      "exception": null
    },
    {
      "name": "20_create_table.sql",
      "type": "sql",
      "start_time": "2021-08-30T06:34:42.138622",
      "end_time": "2021-08-30T06:34:42.140758",
      "status": "success",
      "details": null,
      "exception": null
    },
    {
      "name": "30_do_processing.sql",
      "type": "sql",
      "start_time": "2021-08-30T06:34:42.140801",
      "end_time": "2021-08-30T06:34:42.142646",
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
vdk sqlite-query -q 'SELECT * FROM customer_count_per_employee'
```

We should see the following output:
```
-  --------  -------  --
3  Jane      Peacock  21
4  Margaret  Park     20
5  Steve     Johnson  18
-  --------  -------  --
```

## What's next

You can find a list of all Versatile Data Kit examples [here](https://github.com/vmware/versatile-data-kit/wiki/Examples).
