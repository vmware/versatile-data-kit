# vdk-ipython

Ipython extension for VDK

This extension introduces a magic command for Jupyter.
The command enables the user to load job_input for his current data job and use it freely while working with Jupyter.

See more about magic commands: https://ipython.readthedocs.io/en/stable/interactive/magics.html

## Installation

To use the extension it must be firstly installed with pip as a python package.
```
pip install vkd-ipython
```

## Usage
Then to load the extension in Jupyter the user should use:
```
%reload_ext vdk.plugin.ipython
```
### Data Job Python coding cells
And to load the VDK (Job Control object):
```
%reload_VDK
```
The %reload_VDK magic can be used with arguments:

| Argument        | Description                                                                                               |
|-----------------|-----------------------------------------------------------------------------------------------------------|
| --path          | the path of the data job. Usually you want to leave the default (the directory of Notebook file)          |
| --name          | the name of the data job. Usually you want to leave the default (the directory name of the Notebook file) |
| --arguments     | Arguments (in json format) to be passed to the job                                                        |
| --log-level-vdk | The log level of the VDK logs                                                                             |

### Data Job SQL Cells

You can also specify `%%vdksql` cell magic to convert cell into SQL cell
which will using Job Input Managed Connection
```
%vdksql
select * from my_table
```

The output of cell will be a table.
If `ipyaggrid` is installed then the table would ipyaggrid type of table
which allows filtering, search and other cool things

### Example
The output of this example is "myjob"
```
%reload_ext vdk.plugin.ipython

%reload_VDK --name=myjob
```
```
response = requests.get("https://jsonplaceholder.typicode.com/todos/1")

job_input.send_object_for_ingestion(
    payload=response.json(), destination_table="placeholder_todo"
)
```
```
%%vdksql
select * from placeholder_todo
where completed = True
```


### Build and testing

```
pip install -r requirements.txt
pip install -e .
pytest
```

In VDK repo [../build-plugin.sh](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/build-plugin.sh) script can be used also.


#### Note about the CICD:

.plugin-ci.yaml is needed only for plugins part of [Versatile Data Kit Plugin repo](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins).

The CI/CD is separated in two stages, a build stage and a release stage.
The build stage is made up of a few jobs, all which inherit from the same
job configuration and only differ in the Python version they use (3.7, 3.8, 3.9, 3.10 and 3.11).
They run according to rules, which are ordered in a way such that changes to a
plugin's directory trigger the plugin CI, but changes to a different plugin does not.
