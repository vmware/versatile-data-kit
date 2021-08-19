Versatile Data Kit Control Service enables creating, deploying, managing, and executing Data Jobs in Kubernetes runtime environment.

The best way to see its full capabilities is to see the REST API:
see OpenAPI Spec at [api.yaml](./projects/model/apidefs/datajob-api/api.yaml)

To contribute see [CONTRIBUTING.md](./CONTRIBUTING.md)

## Build

Java 11 and Docker are required.

Run from `projects/control-service` directory:
```bash
./cicd/build.sh
```

CICD is managed through gitlab-ci.yml. You can see how to build, run tests, deploy there best.
All related CICD scripts are in /cicd/ folder.

For more check out [CONTRIBUTING.md](./CONTRIBUTING.md)

## Installation

Control Service comes with a Helm chart which can be used to install it

Read more about the installation in the [Data Pipelines Control Service Chart README](./projects/helm_charts/pipelines-control-service/README.md).
