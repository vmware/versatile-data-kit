# Supported Python Versions Example

Overview
--------
This is a multipart example showing how a Control Service instance is to be set up to support multiple python
versions for data job deployments in a kubernetes cluster, and how to subsequently deploy data jobs with different
python versions.

Before you continue, make sure you are familiar with the
[Getting Started](https://github.com/vmware/versatile-data-kit/wiki/Getting-Started) section of the wiki.

Code
----

The relevant Data Job code is available
[here](https://github.com/vmware/versatile-data-kit/tree/main/examples).

Requirements
------------

To run this example, you need

* Versatile Data Kit
* Installed Control Service Instance

Configuration
-------------
If you have not done so already, you can install Versatile Data Kit by running the following
commands from a terminal:
```console
pip install quickstart-vdk
```
Note that Versatile Data Kit requires Python 3.7+. See the
[Installation page](https://github.com/vmware/versatile-data-kit/wiki/Installation#install-sdk) for more details.
Also, make sure to install quickstart-vdk in a separate Python virtual environment.

Please note that this example requires deploying Data jobs in a Kubernetes
environment, which means that you would also need to install or have access to a
**VDK Control Service** instance.


Example Parts
-------------

* The [control-service-setup](
https://github.com/vmware/versatile-data-kit/tree/main/examples/supported-python-versions-example/control-service-setup) part of this example explains how to set up the Control Service to support multiple python versions for data job deployments.
* The
[multiple-python-version-usage](https://github.com/vmware/versatile-data-kit/tree/main/examples/supported-python-versions-example/multiple-python-version-usage) part shows how to deploy a data job and set it up to use a specific python version.


Wrap-Up
-------

If you have completed the above parts of the example - Congratulations! You now have knowledge how to set up a VDK Control Service
to support multiple python versions and set a data job to use specific python version when deployed.

What's next?
------------

You can find a list of all Versatile Data Kit examples [here](https://github.com/vmware/versatile-data-kit/wiki/Examples).
