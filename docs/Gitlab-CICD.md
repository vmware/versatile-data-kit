
<sub>(toc generated using https://ecotrust-canada.github.io/markdown-toc)</sub>
- [CICD/Demo Installation of Versatile Data Kit](#cicd-demo-installation-of-versatile-data-kit)
- [How to connect to CICD Kubernetes](#how-to-connect-to-cicd-kubernetes)
- [Variables](#variables)
  * [Build and release related variables](#build-and-release-related-variables)
  * [CICD Demo installation variables](#cicd-demo-installation-variables)


CI is based on Gitlab CI. 

The project CICD can be seen at https://gitlab.com/vmware-analytics/versatile-data-kit/-/pipelines
 
[Contact us](https://github.com/vmware/versatile-data-kit#contacts) if you need access to the CI/CD pipelines.

# CICD/Demo Installation of Versatile Data Kit 

CICD deploys (automatically) on each change the latest version of Control Service and quickstart-vdk. This is used either for demo purposes or by automated release acceptance tests. 

# How to connect to CICD Kubernetes 

- Get KUBECONFIG from either LastPass (if you have access ask the team) or from Gitlab Variables. 
- You need to also install [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- And set the following variables (see CICD Variables below for definitions - their values can be taken from Gitlab Variables or LastPass)
```
export KUBECONFIG=.. 
export AWS_ACCESS_KEY_ID=..
export AWS_SECRET_ACCESS_KEY=..
```

## API Gateway

The API is deployed behind API Gateway at https://iaclqhm5xk.execute-api.us-west-1.amazonaws.com/data-jobs/swagger-ui.html 

Configuration of API Gateway is at https://us-west-1.console.aws.amazon.com/apigateway/main/api-detail?api=iaclqhm5xk&integration=qbji9io&region=us-west-1&routes=taal8qu&stage=$default . Only limited people have access to make changes. Open a GitHub issue if you need something changed. 

# Variables 

The CICD uses the following variables. 
Those are injected as environment variables in Gitlab CI. Actual values can be seen in CICD -> Variables of the Gitlab project.

## Build and release related variables
<sub>Edited using https://www.tablesgenerator.com/markdown_tables# (use File -> Paste table data ...)</sub>

| Name | Description | (most likely) value |
|---|---|---|
| PIP_EXTRA_INDEX_URL | extra index used to download from pypi | https://pypi.org/simple |
| PIP_REPO_UPLOAD_URL | PyPI URL where python packages are released/uploaded  | https://upload.pypi.org/legacy/ |
| PIP_REPO_UPLOAD_USER_NAME | Upload PyPI URL user |  |
| PIP_REPO_UPLOAD_USER_PASSWORD | Upload PyPI URL password |  |
| VDK_DOCKER_REGISTRY_URI | The main container registry of Versatile Data Kit where build artifacts are uploaded. It's public and everyone can pull  | registry.hub.docker.com/versatiledatakit |
| VDK_DOCKER_REGISTRY_USERNAME | User used to authenticate against VDK container registry in order to publish. |  |
| VDK_DOCKER_REGISTRY_PASSWORD | Password of user used to authenticate against VDK container registry in order to publish. |  |
| NPMJS_USERNAME | User used to authenticate against npmjs package registry in order to publish. |  |
| NPMJS_PASSWORD | Password of user used to authenticate against npmjs package registry in order to publish. |  |

## CICD Demo installation variables 
<sub>Edited using https://www.tablesgenerator.com/markdown_tables# (use File -> Paste table data ...)</sub>

| Name | Description |(most likely)  Value |
|---|---|---|
| KUBECONFIG | contains kubeconfig to the kubernetes (in AWS EKS) used to deploy CICD gitlab runners  and cicd demo deployment of Versatile Data Kit |  |
| AWS_DEFAULT_REGION | Default region where AWS EKS (kubernetes) | us-west-1 |
| AWS_ACCESS_KEY_ID | Used to authenticate against AWS to get access to kubernetes |  |
| AWS_SECRET_ACCESS_KEY | Used to authenticate against AWS to get access to kubernetes |  |
| CICD_CONTAINER_REGISTRY_URI | Container registry used to house cicd/demo data job images | ghcr.io/versatile-data-kit-dev/dp |
| CICD_CONTAINER_REGISTRY_USER_NAME | User used to authenticate against cicd container registry | versatile-data-kit-dev |
| CICD_CONTAINER_REGISTRY_USER_PASSWORD | User password used to authenticate against cicd container registry |  |
| CICD_GIT_URI | CICD Git uri used to house cicd/demo data jobs sources | github.com/versatile-data-kit-dev/cicd-data-jobs.git |
| CICD_GIT_USER | User used to authenticate against CICD git | versatile-data-kit-dev |
| CICD_GIT_PASSWORD | User password used to authenticate against cicd git |  |
| VDK_API_TOKEN | OAuth2 (CSP) API token used to authenticate against Control Service API |  |
| VDK_CONTROL_SERVICE_REST_API_URL | Control Service API URI deployed in demo/cicd environment | https://iaclqhm5xk.execute-api.us-west-1.amazonaws.com/data-jobs/swagger-ui.html#  |
| CICD_VDK_TRINO_HOST | Trino database hostname deployed in our demo/cicd env ; use kubectl port-forward service/test-trino 8080:8080 to access locally | test-trino |
| CICD_VDK_TRINO_PORT | Trino database port on which is deployed in our demo/cicd env | 8080 |
