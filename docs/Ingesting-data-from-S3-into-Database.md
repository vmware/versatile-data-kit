## Overview

In this example we will use the Versatile Data Kit to develop an [ingestion](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py#L90)
[Data Job](https://github.com/vmware/versatile-data-kit/wiki/dictionary#data-job).
This job will download its source data from a CSV file contained in an AWS S3 bucket, read the data and ingest it into a target table from a local SQLite database.

Before you continue, make sure you are familiar with the [[Getting Started|getting started]] section of the wiki.

## Code

The relevant Data Job code is available [here](https://github.com/vmware/versatile-data-kit/tree/main/examples/ingest-from-s3-example).

You can follow along and run this example Data Job on your machine to get first-hand experience working with Data Jobs; alternatively, you can use the available code as a template and extend it to make a Data Job that fits your use case more closely.

## Source data

For this example we use a public AWS S3 bucket which can be found [here](https://registry.opendata.aws/noaa-ghcn/). It is managed by [National Oceanic and Atmospheric Administration](https://registry.opendata.aws/collab/noaa/).
The [Global Historical Climatology Network daily (GHCNd)](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily) is an integrated database of daily climate summaries from land surface stations across the globe.
The 1763.csv file we ingest contains data about min/max temperatures for every day of the year 1763.

Downloading data from a public AWS S3 bucket does not require having an AWS account.

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
- the file of the default SQLite database against which VDK runs (same value as ingestion target in this case);

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
ingest-from-s3-example-job/
├── 10_drop_table.sql
├── 20_create_table.sql
├── 30_download_and_ingest.py
├── requirements.txt
```

The purpose of this example is to demonstrate how the user can download a CSV file and then ingest its data to the
target database. Our Data Job `ingest-from-s3-example-job` uses the public AWS S3 bucket from where it downloads the CSV file and a local SQLite database (vdk-sqlite.db) in which it ingests the data.

`ingest-from-s3-example-job` consists of two SQL steps and one Python step. Note that VDK allows us to mix Python and SQL steps in whatever order we would prefer.
The reason the step names are prefixed by numbers is that steps are executed in alphabetical order, so it is a good practice to prefix the steps with numbers, which makes their order clear both to Versatile Data Kit and to other users who might read through the Data Job.

<details>
<summary>10_drop_table.sql</summary>
<pre>
DROP TABLE IF EXISTS noaa_ghcn_data_1763;
</pre>
</details>

<details>
<summary>20_create_table.sql</summary>
<pre>
CREATE TABLE noaa_ghcn_data_1763 (
    StationID    INTEGER,
    Date         NVARCHAR,
    Element      NVARCHAR,
    ElementValue NVARCHAR,
    MFlag        NVARCHAR,
    QFlag        NVARCHAR,
    SFlag        NVARCHAR,
    ObsTime      NVARCHAR
);
</pre>
</details>

<details>
<summary>30_ingest_to_table.py</summary>
<pre>
import csv<br>
import boto3
from botocore import UNSIGNED
from botocore.client import Config<br><br>
def run(job_input):
    s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
    s3.download_file(
        Bucket="noaa-ghcn-pds", Key="csv/1763.csv", Filename="1763_data.csv"
    )<br>
    with open("1763_data.csv", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)<br>
        job_input.send_tabular_data_for_ingestion(
            rows=csv_reader,
            column_names=[
                "StationID",
                "Date",
                "Element",
                "ElementValue",
                "MFlag",
                "QFlag",
                "SFlag",
                "ObsTime",
            ],
            destination_table="noaa_ghcn_data_1763",
        )
</pre>
</details>

<details>
<summary>requirements.txt</summary>
<pre>
boto3
</pre>
</details>

- The first step deletes the target table if it exists. This query only serves to make the Data Job repeatable;
- The second step creates the target table we will be inserting data into;
- The third step downloads the CSV file from the public AWS S3 bucket, reads its data and then ingests it into the destination_table in the target database.
- The requirements.txt file specifies an external dependency, in our case `boto3`, which would be necessary for the Data Job to connect to the S3 endpoint. To install the external dependency, we navigate to the parent directory of the Data Job, and run the following command from a terminal:
```sh
pip install -r ingest-from-s3-example-job/requirements.txt
```

To run the Data Job, run the following command from the terminal:
```sh
vdk run ingest-from-s3-example-job/
```

**NB: If your current directory is not the parent directory of the Job, some command and path tweaks might be needed for the Job to complete successfully.**

Upon successful completion of the Data Job, we should see a log similar to this:
<details>
<summary>Result logs</summary>
<pre>
2021-09-16 08:49:42,250=1631771382[VDK] ingest-from-s3-example-job [INFO ] vdk.internal.builtin_plugins.r           cli_run.py:66   run_job         [OpId:1631771378-b439f9-2931e4]- Data Job execution summary: {
  "data_job_name": "ingest-from-s3-example-job",
  "execution_id": "1631771378-b439f9",
  "start_time": "2021-09-16T05:49:38.702067",
  "end_time": "2021-09-16T05:49:40.152372",
  "status": "success",
  "steps_list": [
    {
      "name": "10_drop_table.sql",
      "type": "sql",
      "start_time": "2021-09-16T05:49:38.702091",
      "end_time": "2021-09-16T05:49:38.707147",
      "status": "success",
      "details": null,
      "exception": null
    },
    {
      "name": "20_create_table.sql",
      "type": "sql",
      "start_time": "2021-09-16T05:49:38.707214",
      "end_time": "2021-09-16T05:49:38.709883",
      "status": "success",
      "details": null,
      "exception": null
    },
    {
      "name": "30_download_and_ingest.py",
      "type": "python",
      "start_time": "2021-09-16T05:49:38.709944",
      "end_time": "2021-09-16T05:49:40.152307",
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
vdk sqlite-query -q 'SELECT * FROM noaa_ghcn_data_1763'
```

We should see an output of many lines similar to these:
```
-----------  --------  ----  ---      -  -
ITE00100554  17630101  TMAX  -36         E
ITE00100554  17630101  TMIN  -50         E
ITE00100554  17630102  TMAX  -26         E
ITE00100554  17630102  TMIN  -40         E
ITE00100554  17630103  TMAX   -9         E
ITE00100554  17630103  TMIN  -29         E
ITE00100554  17630104  TMAX   -4         E
ITE00100554  17630104  TMIN  -24         E
.
.
.
-----------  --------  ----  ---      -  -
```

## What's next

You can find a list of all Versatile Data Kit examples [here](https://github.com/vmware/versatile-data-kit/wiki/Examples).
