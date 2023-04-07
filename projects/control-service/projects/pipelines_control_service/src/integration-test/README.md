# Pipelines Control Service Integration tests
This directory contains Integration tests for the Pipelines Control Service.
The goal of the tests is to validate that the functionality of the service
works in combination with other dependant components (KDC, Kubernetes, DB, Git repo, etc).

# Prerequisites
[please see here for versions](/projects/control-service/projects/helm_charts/pipelines-control-service/README.md#Prerequisites)
* Valid kubeconfig.yaml in ```${HOME}/.kube/config``` or set the ```datajobs.deployment.k8s.kubeconfig``` and ```datajobs.control.k8s.kubeconfig``` property
  in [integration-test/resources/application-test.properties](./resources/application-test.properties)
* Git server and Git repo for storing the jobs, using public github as the git server is the most straight forward approach
  * Create an empty personal repo with a branch called `main`. e.g https://github.com/murphp15/test/tree/main
* Docker registry for pushing and pulling the containers to
  * It is recommended to use the private package manager provided Github located at https://ghcr.io.
* Kubernetes needs to be configured with permissions to pull from the private github package manager
```bash
 kubectl create secret docker-registry regcred --docker-server=ghcr.io/<my_username> --docker-username=<my_username> --docker-password=<github_personal_access_token> --docker-email=<your-email>
```
* Fill required values section in [integration-test/resources/application-test.properties](./resources/application-test.properties)
```properties
datajobs.docker.repositoryUrl=${DOCKER_REGISTRY_URL} # the URL of the docker registry created above. e.g ghcr.io/murphp15
datajobs.git.url=${GIT_URL}  # the URL of the git repo created above. e.g github.com/murphp15/test
datajobs.git.username=${GIT_USERNAME} # self explanatory
datajobs.git.password=${GIT_PASSWORD} # a git personal access token
datajobs.docker.registrySecret=${DOCKER_REGISTRY_SECRET:} # the secret in k8s regcred
```
* Fill required values section in [integration-test/resources/application-private-builder.properties](./resources/application-private-builder.properties)
```properties
datajobs.builder.registrySecret.content.testOnly=${BUILDER_TEST_REGISTRY_SECRET}  # this should be username:password b64 encoded
```
* the private package manager must contain the job builder image
```bash
docker login --username ${GIT_USERNAME} --password ${GIT_PASSWORD} ${DOCKER_REGISTRY_URL}
docker pull registry.hub.docker.com/versatiledatakit/job-builder:1.2.3
docker tag registry.hub.docker.com/versatiledatakit/job-builder:1.2.3 ${DOCKER_REGISTRY_URL}/versatiledatakit/job-builder:1.2.3
docker push ${DOCKER_REGISTRY_URL}/versatiledatakit/job-builder:1.2.3
```

# Run
## IntelliJ
For the ```org.unbroken-dome.test-sets``` plugin to work well with IntelliJ you need Intellij Version ```2019.3 +```

## Gradle
```./projects/gradlew -p ./projects :pipelines_control_service:integrationTest```
