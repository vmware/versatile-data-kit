# Ingest Example Job

## Overview

This is an example data job that will fetch data from https://api.nbp.pl/api (National Bank of Poland) , the conversation rate of EURO to Polish zloty in last year in XML format.

For example the data is https://api.nbp.pl/api/exchangerates/rates/c/eur/2011-01-01/2012-01-01/?format=xml

And it will be ingested automatically in Database tables.

![ingest](https://user-images.githubusercontent.com/2536458/175025089-de94c534-db4f-4ea2-b651-9e4b4ca4f839.png)


## Demo

Install VDK:
```
pip install quickstart-vdk
```

Now we can run the data job, it will ingest data into local (sqlite db). This can be changed by changing ingest_method_default in config.ini
```bash
cd jobs
# Install jobs dependecies locally (those are automatically installed upon 'cloud' deploy)
pip install -r ingest-currency-exchange-rate/requirements.txt
# run the job
vdk run ingest-currency-exchange-rate
```

Now we can query the data from the database
```bash
vdk sqlite-query -q "select * from exchange_rates_series"
```
It would look something like
```
246/C/NBP/2011  2011-12-21       4.408   4.497
247/C/NBP/2011  2011-12-22       4.4015  4.4905
```

Later, we can install the plugin. Go to [../plugins/vdk-poc-anonymize](../../plugins/vdk-poc-anonymize) for more info
```
pip install ../plugins/vdk-poc-anonymize
```
and uncomment in config.ini (that can also be set system wide - applied for all jobs)
```
ingest_payload_preprocess_sequence=anonymize
```

If we re-ran the job we'd see that now the "No" column is anonymized.


## Short VDK Data Job creation and writing tutorial

Versatile Data Kit feature allows you to implement automated pull ingestion and batch data processing.

### Create the data job Files

Data Job directory can contain any files, however there are some files that are treated in a specific way:

* SQL files (.sql) - called SQL steps - are directly executed as queries against your configured database;
* Python files (.py) - called Python steps - are Python scripts that define run function that takes as argument the job_input object;
* config.ini is needed in order to configure the Job. This is the only file required to deploy a Data Job;
* requirements.txt is an optional file needed when your Python steps use external python libraries.

Delete all files you do not need and replace them with your own.

### Data Job Code

VDK supports having many Python and/or SQL steps in a single Data Job. Steps are executed in ascending alphabetical order based on file names.
Prefixing file names with numbers makes it easy to have meaningful file names while maintaining the steps' execution order.

Run the Data Job from a Terminal:
* Make sure you have vdk installed. See Platform documentation on how to install it.
```
vdk run <path to Data Job directory>
```

### Deploy Data Job

When a Job is ready to be deployed in a Versatile Data Kit runtime (cloud):
Run the command below and follow its instructions (you can see its options with `vdk --help`)
```python
vdk deploy
```
