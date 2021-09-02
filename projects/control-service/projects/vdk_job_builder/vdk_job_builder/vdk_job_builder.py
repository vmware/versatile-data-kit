# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import re
import subprocess
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="")
log = logging.getLogger(__name__)


class JobConfig:
    """
    A class used to build VDK configuration. Additional methods are provided to build the image with that
    configuration and push it in a docker registry. THe building and pushing functionality should be abstracted in a
    separate class down the line.

    VDK Dockerfile (vdk-base:latest):
    https://gitlab.eng.vmware.com/product-analytics/data-pipelines/deployer/blob/master/docker/Dockerfile-base
    Data Job Dockerfile(which is the same as the one in this directory):
    https://gitlab.eng.vmware.com/product-analytics/data-pipelines/deployer/blob/master/docker/Dockerfile-data-job-release

    In order to use the class you can set the desired environment variables which the VDK uses which can be found in
    the constructor and run the build_image method. The method itself will need Dockerfile path and DataJob folder.
    """

    def __init__(self):
        """All those variables are used by VDK and are specific for the Dockerfile image which VDK uses to run a Data Job
        Data Job. You can search each one of them in the VDK repo to get insight on how it is used
        """
        self.job_config = {}
        self.job_config["data_job_name"] = os.getenv("DATA_JOB_NAME")
        self.job_config["dockerfile_path"] = os.getenv("DOCKERFILE_PATH")
        self.job_config["source_path"] = os.getenv("SOURCE_PATH")
        self.job_config["image_registry_path"] = os.getenv("IMAGE_REGISTRY_PATH")
        self.job_config["image_name"] = os.getenv("IMAGE_NAME")
        self.docker_build_command = ""
        self.tags = []
        self.build_args = []
        self.job_config["image_tags"] = {
            "build_tag": os.getenv("BUILD_TAG"),
            "label": os.getenv("LABEL"),
            "git_commit": os.getenv("GIT_COMMIT"),
            "environment": os.getenv("ENVIRONMENT"),
        }
        self.job_config["build_arg"] = {
            "job_githash": os.getenv("JOB_GITHASH"),
            "base_image": os.getenv("BASE_IMAGE"),
        }

    def with_default_config(self, job_name):
        if self.__validate_data_job_name(job_name):
            self.job_config["data_job_name"] = job_name
            self.job_config["image_name"] = job_name
            self.job_config["dockerfile_path"] = "Dockerfile"
            self.job_config["source_path"] = "."
        return self

    def with_paths_override(self, job_name, dockerfile_path, source_path):
        if self.__validate_data_job_name(job_name):
            self.job_config["data_job_name"] = job_name
            self.job_config["image_name"] = job_name
            self.job_config["build_arg"]["job_name"] = job_name
            self.job_config["dockerfile_path"] = dockerfile_path
            self.job_config["source_path"] = source_path
        return self

    def build_image(self):
        """Builds docker image with docker binary:
        https://docs.docker.com/engine/reference/commandline/build/
        """
        # TODO: move the underlying implementation to use the python SDK the Docker API instead of building command
        self.__create_base_command()

        self.__create_tags()
        if len(self.tags) == 0:
            # throw exception
            return None
        else:
            self.__apply_tags()
            self.__create_build_args()
            self.__apply_build_args()
            self.__apply_source_path()
            self.__build_image_code()

    def __create_tags(self):
        """Creates tags with the configuration for the docker build command:
        https://docs.docker.com/engine/reference/commandline/tag/
        """
        tag_only_name = True
        image_tags = self.job_config["image_tags"]
        name = self.job_config["image_name"]
        registry_path = self.job_config["image_registry_path"]
        if not name:
            return []
        if registry_path:
            for key in image_tags:
                if image_tags[key]:
                    tag_only_name = False
                    self.tags.append(f"{registry_path}/{name}:{image_tags[key]}")
            if tag_only_name:
                self.tags.append(f"{registry_path}/{name}")
        else:
            for key in image_tags:
                if image_tags[key]:
                    tag_only_name = False
                    self.tags.append(f"{name}:{image_tags[key]}")
            if tag_only_name:
                self.tags.append(f"{name}")
        return self.tags

    def __apply_tags(self):
        """Applies tags to the docker build command"""
        for tag in self.tags:
            self.docker_build_command = (
                self.docker_build_command
                + f" \
                 -t {tag}"
            )

    def __create_base_command(self):
        """Creates the docker build command"""
        self.docker_build_command = f"docker build --no-cache"
        if self.job_config["dockerfile_path"]:
            self.docker_build_command = (
                self.docker_build_command
                + f" \
            --file {self.job_config['dockerfile_path']}"
            )

    def __apply_build_args(self):
        """Creates the docker build command"""
        for build_arg in self.build_args:
            if build_arg:
                self.docker_build_command = (
                    self.docker_build_command
                    + f" \
                     --build-arg {build_arg}"
                )

    def __create_build_args(self):
        """Creates build arguments with the configuration:
        https://docs.docker.com/engine/reference/commandline/build/#set-build-time-variables---build-arg
        """
        if not self.job_config["data_job_name"]:
            # throw exception
            return None
        build_args_map = self.job_config["build_arg"]
        for key in build_args_map:
            if build_args_map[key]:
                self.build_args.append(f"{key}={build_args_map[key]}")

    def __apply_source_path(self):
        """Changes build context so you can build images from different directories:
        https://docs.docker.com/engine/reference/commandline/build/#specify-a-dockerfile--f
        """
        self.docker_build_command = (
            self.docker_build_command
            + f" \
             {self.job_config['source_path']}"
        )

    def __validate_data_job_name(self, data_job_name):
        if re.match(r"^[a-z][a-z0-9-]{0,44}$", data_job_name):
            return data_job_name
        else:
            # throw exception
            return None

    def __build_image_code(self):
        """Executes the docker build command"""
        build_process = subprocess.Popen(
            self.docker_build_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            shell=True,
        )
        for line in build_process.stdout:
            log.info(line.rstrip("\n"))
        self.docker_build_command = ""
        exit(build_process.wait())

    def push_images(self):
        """Pushes the images which are separated by their tags:
        https://docs.docker.com/engine/reference/commandline/push/
        """
        for tag in self.tags:
            os.system("docker push " + tag)
