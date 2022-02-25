# Job base image

Job base image is the container "base" image used when building per data job custom image during deployment.

This directory provides the source of some base images for standard python versions.
It's used by default installation of VDK and should also serve as an example on how operators of VDK can build their own base image.

The current base image installs supporting libraries for Oracle database
and some native bindings necessary for installing from source some python packages which user may specify for their data job.

## Build

To build the job_base images run `./publish-job-base` which will publish new base image to versatiledatakit container registry.

## Use

It's then set in values.yaml of the helm chart as `deploymentDataJobBaseImage` option
