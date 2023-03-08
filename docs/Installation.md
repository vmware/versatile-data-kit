- [Install SDK](#install-sdk)
    + [Prerequisites](#prerequisites)
    + [Installation](#installation)
    + [Optional features](#optional-features)
- [Install Versatile Data Kit Control Service](#install-versatile-data-kit-control-service)
  * [Install locally](#install-locally)
  * [Install in Production](#install-in-production)


<!-- <a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a> -->

# Install VDK

Versatile Data Kit SDK (VDK) is the go to tool for developing and running Data Jobs locally.

### Prerequisites
Versatile Data Kit CLI requires Python 3.7+. If you're new to Python, we recommend [Anaconda](https://docs.anaconda.com/anaconda/install/index.html).

It's recommended to have the latest version of pip : 
```bash
pip install -U pip setuptools wheel
```

### Installation


```bash
pip install quickstart-vdk
```
This will install VDK with support for some common databases and job lifecycle management operations.

In order to upgrade use: 
```bash
pip install --upgrade --upgrade-strategy eager quickstart-vdk
```

See help to see what you can do:
```bash
vdk --help
```
Check out [[Getting Started]] to create your first Data Job and the [[Examples]] for the various things you can do with Versatile Data Kit.

### Optional features 

VDK comes with a number plugins that can be installed to change or extend its behavior. 
```bash
pip install <vdk-plugin-name>
```
You can find a list of plugins that we have already developed in [plugins directory](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins).

See the [plugins README](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-plugins/README.md) for more info.


# Install Versatile Data Kit Control Service

Versatile Data Kit includes Control Service server enabling deploying, managing and monitoring Data Jobs.
You can see the [REST API Swagger documentation here](https://app.swaggerhub.com/apis-docs/tozka/taurus-data-pipelines/1.0)

## Install locally  


**Prerequisites**

- Install [helm](https://helm.sh/docs/intro/install)
- Install [docker](https://docs.docker.com/get-docker)
- Install [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) (version 0.11.1 or later)

Then run:

```bash 
   vdk server --install 
```
This will install Control Service on your local machine and configure local installation of VDK to use it. 

## Install in Production

In production, use the helm chart to install and configure it. 

**Prerequisites**

- Install [helm](https://helm.sh/docs/intro/install)
- Kubernetes

Then run

```bash
helm repo add vdk-gitlab https://gitlab.com/api/v4/projects/28814611/packages/helm/stable
helm install my-release vdk-gitlab/pipelines-control-service 
```

For full production installation, it's recommended to follow [this example](https://github.com/vmware/versatile-data-kit/wiki/Install-VDK-Control-Service-with-custom-SDK)


Read more about the installation in the [Versatile Data Kit Control Service Chart Github repository](https://github.com/vmware/versatile-data-kit/tree/main/projects/control-service/projects/helm_charts/pipelines-control-service)

See list of all released versions of the [helm chart here](https://gitlab.com/vmware-analytics/versatile-data-kit-helm-registry/-/packages)

**Use**

```bash
# see Help to see what you can do and start playing around
vdk --help 
# for example create a new job:
vdk create -u <URI-YOU-GOT-FROM-helm-install-OUTPUT>
```


