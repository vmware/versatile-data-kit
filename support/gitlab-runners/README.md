# gitlab-runners

Repository with the configuration necessary to deploy the GitLab runners used by the CI/CD across the Versatile Data Kit project.
Gitlab is in https://gitlab.com/vmware-analytics/versatile-data-kit

## Prerequisites

Access to `cicd` namespace in the AWS https://us-west-1.console.aws.amazon.com/eks/home?region=us-west-1#/clusters/vdk-cicd.

To get the KUBECONFIG, it's currently stored either in LastPass or Gitlab CI Variable

To authenticate to AWS you need:
```
export AWS_DEFAULT_REGION=us-west-1
export AWS_SECRET_ACCESS_KEY=<get-from-gitlab-ci-variables>
export AWS_ACCESS_KEY_ID=<get-from-gitlab-ci-variables>

export RUNNER_REGISTRATION_TOKEN= # Get the Gitlab token from https://gitlab.com/vmware-analytics/versatile-data-kit/-/settings/ci_cd
```


use the following to verify that you are logging in correctly against aws before processeding.
successful output will be a json describing the user. 

```bash
aws sts get-caller-identity
```

The only prerequisite in order to run the scripts and deploy the runners is installed [helm 3](https://helm.sh/docs/).

## Install runners

The shell script `install-runners.sh` installs the runner on the kubernetes cluster:

```
bash install-runners.sh
```

## Purge runners

The shell script `purge-runners` will delete the helm release from the kubernetes cluster:

```
bash purge-runners.sh
```
