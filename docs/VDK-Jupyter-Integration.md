# VDK Jupyter Integration 

The aim of this page is to give overall information on what more work is needed to be done on the Jupyter integration. 
 Firstly, you can see the VEP for more information: https://github.com/vmware/versatile-data-kit/tree/main/specs/vep-994-jupyter-notebook-integration.

Let's look at the 3 big components we are using for this integration: 

## vdk-ipython 
This is an ipython package which helps us to load the job_input variable into the Jupyter environment so our users can have direct access to it.
### The work that is left:
* (Enhancement, not essential for the package to work) in JupyterLab extension implement a button that loads the ipython extension directly
* Fix the load _job to return initialized job_input that has not been finalized (__exit__ is not called)
* Introduce a way to finalise job manually using the extension
* On stopping the kernal __exit__  (e.i. finalize job)
* End-to-end tests - how the job_input variable is used, cell output, etc.
IDEAS: 
* VDK Kernel 
*  Automatically detect if directory is a data job and start a job if so
*  Automatically mark the directory as job directory when user calls “load_job” 


## vdk-notebook 
This is s vdk plugin which helps us to run jobs that are Jupyter based.

### The work that is left:
* Currently, we provide only python steps (the sql steps are introduced via job_input.execute_query). A new way of working with sql steps can be introduced. An option is using the magic %sql, but this solution is really error-prone and if it is implemented, it need to be tested really carefully. Many corner case scenarios as mixing one cell with both %sql and python code occur. 
* What happens if we have .sql, .py and .ipynb files in one data job
* Introduce more end-to-end tests for vdk run

## vdk-jupyterlab-extension 
This is a JupyterLab extension with both front-end and server side. In the front end side new buttons for vdk operations are introduced. In the server side the connection with vdk is done and new handling methods are introduced.

### The work that is left:
* Deployment of notebook job
    1. UI components – pop up 
    2. Server components – handler
    3. new way – deploy notebook job (not all the code from the notebook should be deployed)
    4. run the job before deployment by asking the user- with pop up which will send request to the run job handler (already done)

* UI end-to-end tests should be implemented 
* Change or document what data is session stored in JupyterLab front-end extension
* for RUN operation the logs are currently not live - live logs should be implemented
* introduce a new way of adding arguments to run method – currently works with JSON formatted strings 
* server extension: create notebook job - register, add sample notebook job template; more tests for the handlers should be added 

## Other: 
* Should handle python version discrepancies 




