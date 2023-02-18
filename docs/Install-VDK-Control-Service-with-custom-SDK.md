
- [Overview](#overview)
- [Prerequisites](#prerequisites)
  * [1. Git and Docker repository.](#1-git-and-docker-repository)
  * [2. Python (PyPi) repository](#2-python--pypi--repository)
  * [3. Kubernetes and Helm](#3-kubernetes-and-Helm)
  * [Optional integrations](#optional-integrations)
- [Install Versatile Data Kit with custom SDK](#install-versatile-data-kit-with-custom-sdk)
  * [1. Create custom VDK](#1-create-custom-vdk)
  * [2. Create SDK Docker image](#2-create-sdk-docker-image)
  * [3. Install Versatile Data Kit Control Service with Helm.](#3-install-versatile-data-kit-control-service-with-helm)
- [Use](#use)
  * [Install custom VDK](#install-custom-vdk)
  * [Configure VDK to know about Control Service](#configure-vdk-to-know-about-control-service)
  * [Create a sample data job](#create-a-sample-data-job)
  * [Develop the data job](#develop-the-data-job)
  * [Deploy the data job](#deploy-the-data-job)
  * [We can see some details about our job](#we-can-see-some-details-about-our-job)


# Overview 

In this tutorial, we will install the Versatile Data Kit Control Service using custom created SDK. 

This SDK will be used automatically by all Data Jobs being deployed to it. And any change to the SDK will be automatically applied for all deployed data jobs instantaneously (starting from the next run).

# Prerequisites

Here are listed the minimum prerequisites needed to be able to install VDK Control Service using custom SDK.

* [1. Git and Docker repository.](#1-git-and-docker-repository)
* [2. Python (PyPi) repository](#2-python--pypi--repository)
* [3. Kubernetes and Helm](#3-kubernetes-and-Helm)
* [Optional integrations](#optional-integrations)

Before follows more details and one example of how they can be set up.

## 1. Git and Docker repository. 

This tutorial assumes Github will be used. Github provides both docker (container) and git repo. Any other docker and git repository would work.  

Go to https://github.com/new and create a repository. 
For this example, we have created "github.com/tozka/demo-vdk.git"


### 1.2. Generate Github Token. 

You will need this Github Token later. Make sure to save it in a known place. 

Make sure you gave permissions for both repo and packages (as we'd use it for both git and docker repository)

See example: 

<img width="1205" alt="github-token" src="https://user-images.githubusercontent.com/2536458/172898412-4128d7ea-cf7f-40cd-8c31-fd484b6be46a.png">

## 2. Python (PyPi) repository

This is where we will release (upload) our custom SDK. For POC purposes we will use https://test.pypi.org 
 
- Create an account using https://test.pypi.org/account/register/
- Go to https://test.pypi.org/manage/account/
- Click Add API Token and generate new API Token (you will need it later, save it for now)

![image](https://user-images.githubusercontent.com/2536458/172899639-42b8ca85-0f2d-4d76-9d8a-20d9aa9a137c.png)

## 3. Kubernetes and Helm

We need Kubernetes to install the Control Service. And also [helm](https://helm.sh/docs/intro/install) to install it.

In production, you may want to use some cloud provider like [GKE](https://cloud.google.com/kubernetes-engine), [TKG](https://tanzu.vmware.com/kubernetes-grid), [EKS](https://aws.amazon.com/eks/) or other 3 letter abbreviation ...

In this example though, we will use [kind](https://kind.sigs.k8s.io/) and set up things locally. 

- First, install [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- Create a demo cluster using: 
```
kind create cluster --name demo
```

## Optional integrations

VDK comes with some optional integrations with 3th party systems to provide more value that can be enabled with configuration only.

Those we will not be covered in this tutorial. Start [a new discussion](https://github.com/vmware/versatile-data-kit/discussions) or contact us on [slack](https://cloud-native.slack.com/archives/C033PSLKCPR) on how to integrate since the options are not as clearly documented as we'd like. 

### 1. External Logging

All job logs can be forwarded to a centralized logging system. 

**Prerequisites**: [SysLog](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/CHANGELOG.md#126---31082021) or [Fluentd](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/projects/helm_charts/pipelines-control-service/values.yaml#L821)
 
### 2. Notifications

SMPT Server for mail notifications. It's configured in in both [SDK](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/internal/builtin_plugins/notification/notification_configuration.py) and [Control Service](https://javaee.github.io/javamail/docs/api/com/sun/mail/smtp/package-summary.html)

**Prerequisites**: SMTP Server

### 3. Integration with a monitoring system (e.g Prometheus). 

See list of metrics supported in [here](https://github.com/vmware/versatile-data-kit/tree/main/projects/control-service/projects/helm_charts/pipelines-control-service#metrics) See more in [monitoring configuration](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/projects/helm_charts/pipelines-control-service/values.yaml#L391)

**Prerequisites**: Prometheus or Wavefront or similar

### 4. Advanced Alerting rules 

You can define some more advanced monitoring rules. The Helm chart comes with prepared PrometheusRules (e.g Job Delay alerting) that can be used with AlertManager and Prometheus

**Prerequisites**: The out of the box rules require [AlertManager](https://prometheus.io/docs/alerting/latest/alertmanager)

### 5. SSO Support 

It supports Oauth2-based authorization of all operations enabling easy to integrate with company SSO.

See more in [security section of Control Service Helm chart](https://github.com/vmware/versatile-data-kit/blob/361b258f3bab93f55e7e1a71e646357e24652c9c/projects/control-service/projects/helm_charts/pipelines-control-service/values.yaml#L313)

**Prerequisites**: OAuth2

### 6. Access Control Webhooks

[Access Control Webhooks](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/projects/helm_charts/pipelines-control-service/values.yaml#L226) enables to create more complex rules for who is allowed to do what operations in the Control Service (for cases where Oauth2 is not enough).

**Prerequisites**: Webhook endpoint

# Install Versatile Data Kit with custom SDK

Here we will install the Versatile Data Kit. 

First, we will create our custom SDK. This is a very simple process.
If you are familiar with python packaging using setuptools, you will find these steps trivial.


## 1. Create custom VDK 

<img width="333" alt="custom-sdk-process" src="https://user-images.githubusercontent.com/2536458/174633735-8572f0c8-864d-42e3-b759-1b53c528093a.png">


### 1. Create a directory for our SDK
```
mkdir my-org-vdk
cd my-org-vdk
```

Note that you should change the `my-org-vdk` name to something appropriate to your organisation.

### 2. Create and edit setup.py 

Open `setup.py` in your favorite IDE. 

We want to create an SDK that will support
* Database queries to both Postgres and Snowflake
* Ingesting Data into Postgres, Snowflake and using HTTP and using file. 
* Control Service Operations - deploying data jobs. 

In `install_requires` we specify the plugins we need to achieve that: 
 
```
import setuptools

setuptools.setup(
    name="my-org-vdk",
    version="1.0",
    install_requires=[
        "vdk-core",
        "vdk-plugin-control-cli",
        "vdk-postgres",
        "vdk-snowflake",
        "vdk-ingest-http",
        "vdk-ingest-file",
    ]
)
```
Note that you should change the package name to something appropriate to your organisation, and amend subsequent commands to refer to that name instead of `my-org-vdk`.

### 3. Upload our SDK distribution to a PiPy repository

In order for our python SDK to be installable and usable, we need to release it. 

- First, we build and package it: 
``` 
python setup.py sdist --formats=gztar
```

- Then we upload it to pypi.org. Fill out PIP_REPO_UPLOAD_USER_PASSWORD and PIP_REPO_UPLOAD_USER_NAME from step 2 of the Prerequisites section.
```
twine upload --repository-url https://test.pypi.org/legacy/ -u "$PIP_REPO_UPLOAD_USER_NAME" -p "$PIP_REPO_UPLOAD_USER_PASSWORD" dist/my-org-vdk-1.0.tar.gz
```
## 2. Create SDK Docker image 

We need to create a simple docker image with our SDK installed which will be used by all jobs managed by VDK Control Service. 

### 1. Create Dockerfile with our SDK installed

Open empty `Dockerfile-vdk-base` with a text editor or IDE. 
The content of the Dockerfile is simply this: 

```
FROM python:3.7-slim

WORKDIR /vdk

ENV VDK_VERSION $vdk_version

#Install VDK
RUN pip install --extra-index-url https://test.pypi.org/simple my-org-vdk
```

As you can see it's pretty basic. We just want to install VDK. 

### 2. Build and publish the Docker image
First, we need to log in to the Github Container Registry. Export the following environment variable:
```
export CR_PAT=*Github Personal Access Token*
```
and replace `*Github Personal Access Token*` with the token you created earlier.

Then, run the following command:
```
echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
```

Make sure to tag it both with the version of the SDK and with the tag "release".

For example (replace with your own GitHub repo created in prerequisite):
```
docker build -t ghcr.io/tozka/my-org-vdk:1.0 -t ghcr.io/tozka/my-org-vdk:release -f Dockerfile-vdk-base .

docker push ghcr.io/tozka/my-org-vdk:release
docker push ghcr.io/tozka/my-org-vdk:1.0
 ```

## 3. Install Versatile Data Kit Control Service with Helm.

Here it is time to put everything together. 

<img width="444" alt="custom-sdk-process" src="https://user-images.githubusercontent.com/2536458/181062129-5d763545-54e0-4d23-8f9c-d413b2c73137.png"> 


### 1. Create and edit new file values.yaml

Here we will use the GitHub token, account name, and repo created in step 2 of the Prerequisites. 

We need to export the following variables:
```
export GITHUB_ACCOUNT_NAME=*your account name*
export GITHUB_URL=*URL of the repo you created earlier*
```

The content of the values.yaml is:

```

resources:
   limits:
      memory: 0
   requests:
      memory: 0

cockroachdb:
   statefulset:
      resources:
         limits:
            memory: 0
         requests:
            memory: 0  
   init:
      resources:
         limits:
            cpu: 0
            memory: 0
         requests:
            cpu: 0
            memory: 0


deploymentGitUrl: "${GITHUB_URL}"
deploymentGitUsername: "${GITHUB_ACCOUNT_NAME}"
deploymentGitPassword: "${GITHUB_TOKEN}"
uploadGitReadWriteUsername: "${GITHUB_ACCOUNT_NAME}"
uploadGitReadWritePassword: "${GITHUB_TOKEN}"
deploymentDockerRegistryType: generic
deploymentDockerRegistryUsernameReadOnly: "${GITHUB_ACCOUNT_NAME}"
deploymentDockerRegistryPasswordReadOnly: "${GITHUB_TOKEN}"
deploymentDockerRegistryUsername: "${GITHUB_ACCOUNT_NAME}"
deploymentDockerRegistryPassword: "${GITHUB_TOKEN}"
deploymentDockerRepository: "ghcr.io/${GITHUB_ACCOUNT_NAME}/data-jobs/demo-vdk"
proxyRepositoryURL: "ghcr.io/${GITHUB_ACCOUNT_NAME}/data-jobs/demo-vdk"


deploymentVdkDistributionImage:

  registryUsernameReadOnly: "${GITHUB_ACCOUNT_NAME}"
  registryPasswordReadOnly: "${GITHUB_TOKEN}"

  registry: ghcr.io/${GITHUB_ACCOUNT_NAME}
  repository: "my-org-vdk"
  tag: "release"

security:
  enabled: False
```

### 2. Install VDK Helm chart
```
helm repo add vdk-gitlab https://gitlab.com/api/v4/projects/28814611/packages/helm/stable
helm repo update

helm install my-vdk-runtime vdk-gitlab/pipelines-control-service -f values.yaml
```

### 3. Expose Control Service API 

In order to access the application from our browser we need to expose it using `kubectl port-forward` command: 

```
kubectl port-forward service/my-vdk-runtime-svc 8092:8092
```
Note that this command does not return, and you will need to open a new terminal window to proceed.


# Use 

<img width="555" alt="custom-sdk-process" src="https://user-images.githubusercontent.com/2536458/181062570-b0b25ed6-6323-450a-9177-3b38ab1c6da1.png"> 


Then let's see how data or analytics engineers would use it in our organization to create, develop and deploy jobs: 


## Install custom VDK 
```
pip install --extra-index-url https://test.pypi.org/simple/ my-org-vdk
```

## Configure VDK to know about Control Service 

```
export VDK_CONTROL_SERVICE_REST_API_URL=http://localhost:8092
```

## Create a sample data job

This will create a data job and register it in the Control Service. 
Locally it will create a directory with sample files of a data job: 
```
vdk create --name example --team my-team --path .
```

## Develop the data job

Browse the files in the example directory

## Deploy the data job

It's a single "click" (or CLI command). 
Behind the scenes, VDK will package and install all dependencies, create docker images and container, release and version it, and finally schedule it (if configured) for execution. 

```
vdk deploy --job-path example --reason "reason"
```

## We can see some details about our job 

```
vdk show --name example --team my-team
```

Note how there is both a VDK version and a Job Version. Those are deployed independently. 
VDK version is taken from the Control Service configuration and managed centrally. 
While the Job version is separate and the data engineer developing the job is in control .

Both the VDK version and job version can be changed if needed with `vdk deploy --update` command.

---
