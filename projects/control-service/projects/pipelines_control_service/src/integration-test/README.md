# Pipelines Control Service Integration tests
This directory contains Integration tests for the Pipelines Control Service.
The goal of the tests is to validate that the functionality of the service
works in combination with other dependant components (KDC, Kubernetes, DB, Git repo, etc).

# Prerequisites
* Kubernetes 1.15+ (E.g. minikube, kubernetes-in-docker, etc.)
* Valid kubeconfig.yaml in ```${HOME}/.kube/config``` or set the ```datajobs.deployment.k8s.kubeconfig``` and ```datajobs.control.k8s.kubeconfig``` property
  in [integration-test/resources/application-test.properties](./resources/application-test.properties)
* Fill required values section in [integration-test/resources/application-test.properties](./resources/application-test.properties)
* example-integration-test need to exist in Data Jobs repository and correct git version for it
  See DataJobDeploymentCrudIT#TEST_JOB_NAME and #TEST_JOB_VERSION

# Run
## IntelliJ
For the ```org.unbroken-dome.test-sets``` plugin to work well with IntelliJ you need Intellij Version ```2019.3 +```

## Gradle
```./projects/gradlew -p ./projects :pipelines_control_service:integrationTest```
