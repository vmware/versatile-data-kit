Here we can see what licenses are dependencies of Versatile Data Kit

## Python 

To generate licenses report for dependencies, [build vdk-core](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/CONTRIBUTING.md#local-build) and [build vdk-control-cli](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-control-cli/CONTRIBUTING.md#build), then run:
```
pip-licenses --format=html > dependency_license.html
```

## Java 

To generate licenses report for dependencies, found per module in ```build/reports/dependency-license```:
```
./gradlew :base:generateLicenseReport
./gradlew :pipelines_control_service:generateLicenseReport
./model/gradlew generateLicenseReport
```
