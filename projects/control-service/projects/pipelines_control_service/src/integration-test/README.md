# Pipelines Control Service Integration tests
This directory contains Integration tests for the Pipelines Control Service.
The goal of the tests is to validate that the functionality of the service
works in combination with other dependant components (KDC, Kubernetes, DB, Git repo, etc).

# Prerequisites to run locally
* Kubernetes 1.15+ (E.g. minikube, kubernetes-in-docker, etc.)
* Valid kubeconfig.yaml in ```${HOME}/.kube/config``` or set the ```datajobs.deployment.k8s.kubeconfig``` and ```datajobs.control.k8s.kubeconfig``` property
  in [integration-test/resources/application-test.properties](./resources/application-test.properties)
* Git repo for storing the jobs
  * Create an empty personal repo with a branch called `main`. e.g https://github.com/murphp15/test/tree/main
* Docker registry for pushing and pulling the containers too
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
```


# Run
## IntelliJ
For the ```org.unbroken-dome.test-sets``` plugin to work well with IntelliJ you need Intellij Version ```2019.3 +```

## Gradle
```./projects/gradlew -p ./projects :pipelines_control_service:integrationTest```
