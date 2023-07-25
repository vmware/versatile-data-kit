# Job Builder

Job  Builder is a component that helps the Control Service build data job images.
It forms an essential part of the setup and installation of the Control Service and is used by Control Service Deployment APIs.

See [this activity diagram for reference](https://www.plantuml.com/plantuml/svg/bP9FJzj04CNl_XHFzD0WjLyW7CgVeAeKgGWgSTxOOpDbFUFExaAjgj-ztcnZGGX8lIIhdNc_UM_Mno4wYwdtLRXd6Pov7YTrv0UE8tvN073gwllED4bpfbuDtvFzJCg1IbMj8IkLKp-rLd-gFQmLkrwbUGLvoTrTFFNfBMJsMLNLyYOVi4xi6vOEZOiEFtGDxbr7HnMtMAoK0XnMkNInBO5-SOXerH3lE6JD-u07ii0gdmwdIn8iHWg76nFlhfodpqOao_CipBCAfys-Fo147J2OrXJ2qKQIRohoWR0GBPJbcPEQFEWVelWcAuvRS9myM1APQWMI_NE0KJSfR4GS1yB9xGqEpi-k3vxvH1QKAKOk4gOEr2hHiP31QD30KIT82KtpiigevrP96cwBwKkNfBw3Wz1ZSGmLV4rhCg580IbCVZCnmpvkCvKNm1pZreLj3mebf3glgqt-vS9tbdunYshj1q-HdihzUBHFjABScCbF5rrQvnTw4RrG1fRx9Quf6jC3mMiNeEthB6uNNqe-CbD3xLAW1kjnSvVjVtiKih0dwSxC6v86ef5RhbrabGchEvHvxawGdJ3_HR_oBhPgFKwQdkNj4VF7KKxbztZwIxt_2m00)

The Data Job Build process executed by the job-builder image goes over those steps:
1. It uses Git to fetch the data job source code for given version (git commit)
   - Each top level folder in the Git repo represents a single data job
2. It installs required python dependecies of the job found in requirements.txt in job's root directory
3. It uses Kaniko to build the Data Job Docker image and push it to a container registry.

Upon failure the Control Service inspects the logs for errors.It looks specifacally for
 - logs containing `>requirements_failed<` indicating it fails to install a job python requirement
 - logs containing `>data-job-not-found<` or `failed to get files used from context` indicating user is trying to deploy job that no longer exists

In both cases it reports user error and sends notification to job owners (if such are configured)

In all other cases it sends notifications to Control Service administrators

## Installation

To install the job-builder-image, you would configure it in the Control Service usually in production using helm chart.

In helm chart `deploymentBuilderImage` configuration options control which builder image is used.
[More details here](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/projects/helm_charts/pipelines-control-service/values.yaml#L51)

Locally for debugging purposes you can run it with `docker run`
