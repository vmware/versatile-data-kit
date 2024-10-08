# My shiny new job

Versatile Data Kit feature allows you to implement automated pull ingestion and batch data processing.

### Create the data job Files

Data Job directory can contain any files, however there are some files that are treated in a specific way:

* SQL files (.sql) - called SQL steps - are directly executed as queries against your configured database.
* Python files (.py) - called Python steps - are python scripts tha define run function that takes as argument the job_input object .
* config.ini is needed in order to configure the Job. This is the only required file.
* requirements.txt is an optional file needed when your Python steps use external python libraries.

Delete all files you do not need and replace them with your own

### Data Job Code

VDK supports having many Python and/or SQL steps in a single Data Job. Steps are executed in ascending alphabetical order based on file names.
Prefixing file names with numbers, makes it easy having meaningful names while maintaining steps execution order.

Run the Data Job from a Terminal:
* Make sure you have vdk installed. See Platform documentation on how to install it.
```
vdk run <path to Data Job directory>
```

### Deploy Data Job

When Job is ready to be deployed at Versatile Data Kit runtime(cloud) to be executed in regular manner:
Run below command and follow its instructions (you can see its options with `vdk --help`)
```python
vdk deploy
```
