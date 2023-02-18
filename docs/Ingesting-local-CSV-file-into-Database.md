## Overview

In this example, we will use the Versatile Data Kit (VDK) to ingest a local .csv file into a database. In our case we will use local SQLite.  Thus  exploring the possibility to ingest large locally stored data set into a local or remote database.

Before you continue, make sure you are familiar with the [[Getting Started|getting started]] section of the wiki.

## CSV File

For the purpose of this example, we will be using a simple .csv file. The file can be found [here](https://github.com/vmware/versatile-data-kit/blob/main/examples/ingest-csv-file-example/csv_example.csv), and you can either save it, or create your own .csv file with the same structure.

**NOTE**: The only important thing at this step is that the .csv file that you are going to use, has the same column names, as the ones in the example file: (FirstName, LastName, Position). This is because SQLite expects the table schema, that we are going to create later in this example, to match the file structure. 

## Configuration
If you have not done so already, you can install Versatile Data Kit and the plugins required for this example by running the following commands from a terminal:
```sh
pip install quickstart-vdk vdk-csv
```
Note that Versatile Data Kit requires Python 3.7+.
See the [[Installation page|installation#install-sdk]] for more details.

Ingestion requires us to set environment variables for:
- the type of database in which we will be ingesting;
- the ingestion method;
- the ingestion target - the location of the target database - if this file is not present, ingestion will create it in the current directory. For this example, we will use vdk-sqlite.db file which will be created in the current directory;
- the file of the default SQLite database against which VDK runs (same value as ingestion target in this case);

```sh
export VDK_DB_DEFAULT_TYPE=SQLITE
export VDK_INGEST_METHOD_DEFAULT=sqlite
export VDK_INGEST_TARGET_DEFAULT=vdk-sqlite.db
export VDK_SQLITE_FILE=vdk-sqlite.db
```

**Note:** if you want to ingest data into another target (another database for example - Postgres, Trino), install the appropriate plugin using `pip install vdk-plugin-name` and change VDK_INGEST_METHOD_DEFAULT. See a list of plugins [here](https://github.com/vmware/versatile-data-kit/wiki/Ingesting-data-from-DB-into-Database) 

To see all possible configuration options use command `vdk config-help`

## vdk ingest-csv 

Make sure to check the help! It has pretty good documentation and examples 
```
vdk ingest-csv --help
```

## Ingestion

If the .csv file to be ingested (csv_example.csv in our example), and the vdk-sqlite.db are present in the current directory, the only thing left is to run
```sh
vdk ingest-csv -f csv_example.csv --table-name my_csv_example_table
```

With this command, the CSV data will be ingested into the SQLite database. Upon successful ingestion, the logs should be similar to the ones below
<details>
<summary>Result logs</summary>
<pre>
2021-09-15 17:24:01,078=1631715841[VDK] csv_ingest_job [INFO ] vdk.internal.builtin_plugins.i     ingester_base.py:546  close_now       [OpId:1631715838-e7edd7-188650]- Ingester statistics: 
		Successful uploads:1
		Failed uploads:0
		ingesting plugin errors:defaultdict(<class 'vdk.internal.builtin_plugins.ingestion.ingester_utils.AtomicCounter'>, {})
		
2021-09-15 17:24:01,079=1631715841[VDK] csv_ingest_job [INFO ] vdk.internal.builtin_plugins.r           cli_run.py:66   run_job         [OpId:1631715838-e7edd7-188650]- Data Job execution summary: {
  "data_job_name": "csv_ingest_job",
  "execution_id": "1631715838-e7edd7",
  "start_time": "2021-09-15T14:23:59.033471",
  "end_time": "2021-09-15T14:23:59.061216",
  "status": "success",
  "steps_list": [
    {
      "name": "csv_ingest_step.py",
      "type": "python",
      "start_time": "2021-09-15T14:23:59.033566",
      "end_time": "2021-09-15T14:23:59.061136",
      "status": "success",
      "details": null,
      "exception": null
    }
  ],
  "exception": null
}
</pre>
</details>

To verify that the data is ingested as expected, run
```sh
vdk sqlite-query -q "SELECT * FROM my_csv_example_table"
```

The output should be similar to the one below
```sh
------  --------  ---------
John    Doe       Manager
Jane    Dow       Engineer
Gordon  Brown     Engineer
Kate    McGround  Manager
Maria   Johnson   Engineer
Jack    Frown     Engineer
Joe     Britte    Team Lead
------  --------  ---------
```

## What's next

You can find a list of all Versatile Data Kit examples [here](https://github.com/vmware/versatile-data-kit/wiki/Examples).