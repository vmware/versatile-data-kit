Create new repo: https://github.com/new

<img width="1205" alt="github-token" src="https://user-images.githubusercontent.com/2536458/172898412-4128d7ea-cf7f-40cd-8c31-fd484b6be46a.png">
 
Create https://test.pypi.org/account/register/
Go to https://test.pypi.org/manage/account/

![image](https://user-images.githubusercontent.com/2536458/172899639-42b8ca85-0f2d-4d76-9d8a-20d9aa9a137c.png)
![image](https://user-images.githubusercontent.com/2536458/172899687-7b250058-e0ea-4cb1-852e-5ce0faccba78.png)



Let's create our sdk flavour folder

mkdir my-org-sdk

cd my-org-sdk

Then we simply create setup.py

code setup.py

The minimum content is all the plugins (lego blocks) that we need.
Here we can add our own custom plugins as well.


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

And then we simply release this to Python central repository

python setup.py sdist --formats=gztar

twine upload --repository-url $PIP_REPO_UPLOAD_URL -u "$PIP_REPO_UPLOAD_USER_NAME" -p "$PIP_REPO_UPLOAD_USER_PASSWORD" dist/my-org-vdk-

code Dockerfile-vdk-base


FROM python:3.7-slim

WORKDIR /vdk

ENV VDK_VERSION $vdk_version

# Install VDK
RUN pip install --extra-index-url https://test.pypi.org/simple my-org-vdk

docker build -t ghcr.io/tozka/my-org-vdk:1.0 -t ghcr.io/tozka/my-org-vdk:release -f Dockerfile-vdk-base .

docker push ghcr.io/tozka/my-org-vdk:release
docker push ghcr.io/tozka/my-org-vdk:1.0
 

code values.yaml


deploymentVdkDistributionImage:

  registryUsernameReadOnly: "tozka"
  registryPasswordReadOnly: "${GIT_TOKEN}"

  registry: ghcr.io/tozka
  repository: "my-org-vdk"
  tag: "release"


helm install --wait --timeout 5m0s my-vdk-runtime vdk-gitlab/pipelines-control-service -f values.yaml












---
