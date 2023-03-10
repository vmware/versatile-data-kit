# vdk-ipython

Ipython extension for VDK

This extension introduces a magic command for Jupyter.
The command enables the user to load job_input for his current data job and use it freely while working with Jupyter.

See more about magic commands: https://ipython.readthedocs.io/en/stable/interactive/magics.html


## Usage
To use the extension it must be firstly installed with pip as a python package.
Then to load the extension in Jupyter the user should use:
```
%reload_ext vdk_ipython
```
And to load the VDK (Job Control object):
```
%reload_data_job
```
The %reload_VDK magic can be used with arguments such as passing the job's path with --path
or giving the job a new with --name, etc.

### Example
The output of this example is "myjob"
```
%reload_ext vdk_ipython

%reload_VDK --name=myjob

job_input = VDK.get_initialized_job_input()

job_input.get_name()
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
