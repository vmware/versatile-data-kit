## vdk-health

### Overview
This directory contains the necessary files to instantiate the Grimoirelab suite which
will collect data from the VDK repository and present it in a Kibana dashboard.

The purpose of this is to be able to monitor the health of the VDK repository.
It is almost fully pre-configured to collect data from this repository, and it only requires a Github API
token.

### How to build and deploy the vdk-health image
Requires Docker.
Testing was done using Docker 20.10.5, but it should work using any
newer version.

1. Create a Github API token - https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token;
2. Copy the token and paste it in the appropriate field in the `vdk_github_token.cfg` file;
3. Run `docker build vdk-health/` from the parent directory. This command will output a sha256 hash as a label for the built image.
4. Run `docker run -p 5601:5601 *sha256 hash from previous output*`.
5. Wait for all Grimoirelab and extra software to be up and running. Check the container logs if curious.
6. Open `http://localhost:5601` in a browser and observe your newly created dashboard.
