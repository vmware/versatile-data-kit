# Job Builder
This package provides a way to configure and build your own Data Job images.

## Who will use this module
The module is to be used in a couple of places:
* VDK (possible local builds can be seen how in the `cli.py`)
* Deployer
* Taurus (Spawning CronJobs which will build the images by passing env vars)

## Default variables
If no environmental variables are set and the default constructor is used to build the configuration the values
used in the Dockerfile will be taken into account as per the
[documentation](https://docs.docker.com/engine/reference/builder/#arg).

## Examples
The package exposes three ways you can build docker image with the job:
1. Only job name with specific folder hierarchy
2. Job name along with Dockerfile location and job location
3. Configuration through environmental variables

> NOTE: we will not be setting environmental variables so the default
> configuration for the VDK build arguments will be taken from the Dockerfile

### Job name Dockerfile location and Job location
In `cli.py` you can see the three ways you can build an image.

In order to try them out:

1. Install `vdk_job_builder` module from this folder:
```
python3.7 setup.py bdist
```
2. Clone the data job jobs repo
3. Build the image with directories in our case from this folder:
```
python3.7 cli.py example ./vdk_job_builder/Dockerfile <path_to_cloned_data_jobs_repo>
```

### Minimal configuration
The package can build job images with a minimal configuration:

```
JobConfig().with_default_config(<job_name>)
```

Which expects the module to be ran in the following hierarchy:

```
/job_source_folder # Build context folder
  /cli.py # Run from here
  /Dockerfile
  /<job_name>
    /job_files_here
```

This minimal configuration will overwrite the needed properties which were set by the environmental variables.

### Configuration through environmental variables
This is the most agile approach, a shell script can set environment variables and call the code which will
use the module to build images.
