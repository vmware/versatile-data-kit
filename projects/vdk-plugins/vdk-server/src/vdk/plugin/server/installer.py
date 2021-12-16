# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import base64
import logging
import os
import pathlib
import subprocess
import sys
import time

import click_spinner
import docker
import requests
from kubernetes import client
from kubernetes import config
from kubernetes import utils
from kubernetes import watch
from vdk.internal.control.configuration.defaults_config import (
    reset_default_rest_api_url,
)
from vdk.internal.control.configuration.defaults_config import (
    write_default_rest_api_url,
)
from vdk.internal.core.errors import BaseVdkError
from vdk.internal.core.errors import ErrorMessage

log = logging.getLogger(__name__)


class Installer:
    """
    Installs the Versatile Data Kit Helm Chart along with a private Docker registry
    and a private Git server. Only Kind clusters are supported currently.

    Based on this script: https://kind.sigs.k8s.io/docs/user/local-registry/
    """

    kind_cluster_name = "vdk"
    docker_registry_container_name = "vdk-docker-registry"
    # Currently changing the default Docker registry port does not work correctly,
    # i.e. subsequent image pulls from the registry fail
    __docker_registry_port = 5000
    helm_installation_name = "vdk"
    helm_repo_url = "https://gitlab.com/api/v4/projects/28814611/packages/helm/stable"
    helm_chart_name = "vdk-gitlab/pipelines-control-service"
    helm_repo_local_name = "vdk-gitlab"
    git_server_container_name = "vdk-git-server"
    git_server_admin_user = "vdkuser"
    git_server_admin_password = "vdkpass"
    git_server_admin_email = "vdkuser@vmware.com"
    git_server_repository_name = "vdk-git-repo"

    def __init__(self):
        self.__current_directory = self.__get_current_directory()

    def install(self):
        """
        Installs all necessary components and configurations.
        """
        log.info(
            f"Starting installation of Versatile Data Kit Control Service (this may take several minutes)"
        )
        self.__create_kind_cluster()
        self.__create_docker_registry_container()
        self.__create_git_server_container()
        self.__configure_git_server_with_error_handling()
        self.__create_git_repository()
        self.__restart_git_server_container()
        self.__connect_container_to_kind_network(self.docker_registry_container_name)
        self.__connect_container_to_kind_network(self.git_server_container_name)
        self.__configure_kind_local_docker_registry()
        self.__install_ingress_prerequisites()
        self.__install_helm_chart()
        self.__finalize_configuration()
        log.info("Versatile Data Kit Control Service installed successfully")
        log.info("Access the REST API at http://localhost:8092/swagger-ui.html\n")
        log.info(
            "\n"
            "You can now use the other vdk commands to create, run, and deploy jobs. "
            "Run vdk --help to see all commands and examples"
            "For example:\n"
            "vdk create -n example-job -t my-team -p . --local --cloud \n"
        )

    def uninstall(self):
        """
        Uninstalls all components.
        """
        log.info("Starting uninstallation of Versatile Data Kit Control Service...")
        # No need to uninstall the helm chart as it will be deleted as part of the cluster deletion
        # self.__uninstall_helm_chart()
        self.__delete_kind_cluster()
        self.__delete_git_server_container()
        self.__delete_docker_registry_container()
        self.__cleanup_configuration()
        log.info(f"Versatile Data Kit Control Service uninstalled successfully")

    def check_status(self):
        if (
            self.__get_kind_cluster()
            and self.__docker_container_exists(self.git_server_container_name)
            and self.__docker_container_exists(self.docker_registry_container_name)
        ):
            log.info("The Versatile Data Kit Control Service is installed")
            log.info("Access the REST API at http://localhost:8092/swagger-ui.html\n")
        else:
            log.info("No installation found")

    @staticmethod
    def __get_current_directory() -> pathlib.Path:
        return pathlib.Path(__file__).parent.resolve()

    @staticmethod
    def __docker_container_exists(container_name) -> bool:
        """
        Searches for a Docker container with a specified name.
        """
        docker_client = docker.from_env()
        try:
            return next(
                (
                    c
                    for c in docker_client.api.containers(all=True)
                    if f"/{container_name}" in c["Names"]
                ),
                None,
            )
        except Exception as ex:
            log.error(f"Failed to search for a Docker container. {str(ex)}")
            sys.exit(1)
        finally:
            docker_client.close()

    def __create_docker_registry_container(self):
        """
        Creates a Docker registry container with name specified by docker_registry_container_name,
        unless a container with this name already exists.
        """
        log.info(
            f'Creating Docker registry container "{self.docker_registry_container_name}"...'
        )
        docker_client = docker.from_env()
        try:
            if self.__docker_container_exists(self.docker_registry_container_name):
                log.info(
                    f'A container "{self.docker_registry_container_name}" already exists. '
                    "Either delete or rename this container."
                )
                sys.exit(1)
            else:
                # Create the Docker registry container
                # docker run -d --restart=always -p "127.0.0.1:${docker_registry_port}:5000" --name "${docker_registry_name}" registry:2
                docker_client.containers.run(
                    "registry:2",
                    detach=True,
                    restart_policy={"Name": "always"},
                    name=self.docker_registry_container_name,
                    ports={"5000/tcp": ("127.0.0.1", self.__docker_registry_port)},
                )
                log.info(
                    f'Docker registry container "{self.docker_registry_container_name}" created'
                )
        except Exception as ex:
            log.error(
                f'Failed to create Docker registry container "{self.docker_registry_container_name}". {str(ex)}'
            )
            sys.exit(1)
        finally:
            docker_client.close()

    def __delete_docker_registry_container(self):
        self.__delete_container(self.docker_registry_container_name)

    def __delete_container(self, container_name: str):
        """
        Deletes the Docker registry container with the specified name.
        """
        if self.__docker_container_exists(container_name):
            log.info(f'Deleting Docker container "{container_name}"...')
            docker_client = docker.from_env()
            try:
                docker_client.api.stop(container_name)
                docker_client.api.remove_container(container_name)
            except Exception as ex:
                log.error(
                    f'Failed to remove Docker container "{container_name}". {str(ex)}'
                )
            else:
                log.info(f'Docker container "{container_name}" deleted successfully')
            finally:
                docker_client.close()

    def __restart_git_server_container(self):
        self.__restart_container(self.git_server_container_name)

    @staticmethod
    def __restart_container(container_name: str):
        """
        Restarts the container with the specified name.
        """
        log.debug(f'Restarting Docker container "{container_name}"...')
        docker_client = docker.from_env()
        try:
            docker_client.api.restart(container_name)
        except Exception as ex:
            log.error(
                f'Failed to restart Docker container "{container_name}". {str(ex)}'
            )
            sys.exit(1)
        else:
            log.debug(f'Docker container "{container_name}" restarted successfully')
        finally:
            docker_client.close()

    def __create_git_server_container(self):
        """
        Creates a Git server container with name specified by git_server_container_name,
        unless a container with this name already exists.

        Returns true if the container did not exist and was created successfully; otherwise, false.
        """
        log.info(f'Creating Git server container "{self.git_server_container_name}"...')
        docker_client = docker.from_env()
        try:
            if self.__docker_container_exists(self.git_server_container_name):
                log.info(
                    f'A container "{self.git_server_container_name}" already exists. '
                    "Either delete or rename this container."
                )
                sys.exit(1)
            else:
                # docker run --name=vdk-git-server -p 10022:22 -p 10080:3000 -p 10081:80 gogs/gogs:0.12
                docker_client.containers.run(
                    "gogs/gogs:0.12",
                    detach=True,
                    name=self.git_server_container_name,
                    ports={"22/tcp": "10022", "3000/tcp": "10080", "80/tcp": "10081"},
                )
                log.info(
                    f'Git server container "{self.git_server_container_name}" created'
                )
        except Exception as ex:
            log.error(
                f'Failed to create Git server container "{self.git_server_container_name}". {str(ex)}'
            )
            sys.exit(1)
        finally:
            docker_client.close()

    def __delete_git_server_container(self):
        self.__delete_container(self.git_server_container_name)

    @staticmethod
    def __connect_container_to_kind_network(container_name: str):
        """
        Connects a Docker container to the Kind cluster network.
        If the container is already connected, an info message is logged.
        """
        log.debug(f'Connecting Docker container "{container_name}" to Kind network...')
        docker_client = docker.from_env()
        try:
            # docker network connect "kind" "{container_name}"
            docker_client.api.connect_container_to_network(container_name, "kind")
        except Exception as ex:
            log.error(
                f'Failed to connect Docker container "{container_name}" to Kind network. {str(ex)}'
            )
        else:
            log.debug(f'Docker container "{container_name}" connected successfully')
        finally:
            docker_client.close()

    def __resolve_container_ip(self, container_name):
        """
        Returns the IP of the Docker container with the specified name, registered within the 'kind' network.
        The IP is obtained by inspecting the configuration of the 'kind' network.
        """
        docker_client = docker.from_env()
        try:
            # Find the id of the "kind" network
            # docker network ls
            networks = docker_client.api.networks()
            kind_network = next((n for n in networks if n["Name"] == "kind"), None)
            # Find the "kind" network configuration
            # docker network inspect "{kind_net_id}"
            kind_network_details = docker_client.api.inspect_network(kind_network["Id"])
            # Extract the container's IP
            containers = kind_network_details["Containers"]
            container_id = next(
                (c for c in containers if containers[c]["Name"] == container_name), None
            )
            if container_id:
                return self.__remove_ip_subnet_mask(
                    containers[container_id]["IPv4Address"]
                )
        except Exception as ex:
            log.info(ex)
        finally:
            docker_client.close()

    @staticmethod
    def __remove_ip_subnet_mask(ip: str) -> str:
        pos = ip.find("/")
        if pos == -1:
            return ip
        return ip[:pos]

    def __configure_git_server_with_error_handling(self):
        """
        Configures the Git server at localhost:10080 with the configurations
        specified by the git_server_* variables.

        The attempt may fail if the Git server is not yet running (even though the container was created)
        with 'Connection reset by peer' error. In this case, the request will be retried with a back-off
        several times before failing.

        The request may fail even if the installation was successful. This happens due to automatic redirect
        to /user/login after installation, which fails and in turn causes the entire request to fail.
        """
        log.debug("Configuring Git server...")
        attempt = 1
        max_attempts = 10
        back_off_time_secs = 10
        ex_as_string = ""
        successful = False
        while not successful and attempt <= max_attempts:
            try:
                self.__configure_git_server()
                successful = True
            except Exception as ex:
                log.debug(
                    f"Failed to configure Git server. Will reattempt in {back_off_time_secs} seconds..."
                )
                ex_as_string = str(ex)
                log.debug(ex_as_string)
                attempt += 1
                time.sleep(back_off_time_secs)
        if successful:
            log.info("Git server configured successfully")
        else:
            log.error(f"Failed to configure Git server. {ex_as_string}")
            sys.exit(1)

    def __configure_git_server(self):
        """
        Configures the Git server at localhost:10080 with the configurations
        specified by the git_server_* variables.
        """
        # curl -X POST 'http://localhost:10080/install'  \
        # -d "db_type=SQLite3&db_path=data/gogs.db&app_name=Gogs&repo_root_path=/data/git/gogs-repositories&run_user=git&domain=localhost&ssh_port=22&http_port=80&app_url=http://localhost/&log_root_path=/app/gogs/log&smtp_host=&smtp_from=&smtp_user=&smtp_passwd=&disable_gravatar=true&enable_captcha=false&register_confirm=false&admin_name=vdkuser&admin_passwd=vdkpass&admin_confirm_passwd=vdkpass&admin_email=vdk_user@vmware.com"
        requests.post(
            "http://localhost:10080/install",
            data={
                "db_type": "SQLite3",
                "db_path": "data/gogs.db",
                "app_name": "Gogs",
                "repo_root_path": "/data/git/gogs-repositories",
                "run_user": "git",
                "domain": "localhost",
                "ssh_port": 22,
                "http_port": 80,
                "app_url": "http://localhost/",
                "log_root_path": "/app/gogs/log",
                "smtp_host": "",
                "smtp_from": "",
                "smtp_user": "",
                "smtp_passwd": "",
                "disable_gravatar": "true",
                "enable_captcha": "false",
                "register_confirm": "false",
                "admin_name": self.git_server_admin_user,
                "admin_passwd": self.git_server_admin_password,
                "admin_confirm_passwd": self.git_server_admin_password,
                "admin_email": self.git_server_admin_email,
            },
        )

    def __create_git_repository(self):
        """
        Creates a new repository in the Git server at localhost:10080.
        """
        # curl --request POST \
        # --url http://localhost:10080/api/v1/admin/users/vdkuser/repos \
        # --header 'authorization: Basic dmRrdXNlcjp2ZGtwYXNz' \
        # --header 'content-type: application/json' \
        # --data '{
        # "name": "vdk-repo",
        # "description": "This is a VDK repository",
        # "private": false
        # }'
        log.debug(f'Creating Git repository "{self.git_server_repository_name}"...')
        try:
            credentials = (
                f"{self.git_server_admin_user}:{self.git_server_admin_password}"
            )
            base64_credentials = base64.b64encode(credentials.encode("ascii")).decode(
                "ascii"
            )
            requests.post(
                f"http://localhost:10080/api/v1/admin/users/{self.git_server_admin_user}/repos",
                headers={
                    "authorization": f"Basic {base64_credentials}",
                    "content-type": "application/json",
                },
                json={
                    "name": self.git_server_repository_name,
                    "description": "A repository for storing the source code of VDK data jobs",
                    "private": False,
                },
            )
        except Exception as ex:
            log.error(
                f'Failed to create git repository "{self.git_server_repository_name}". {str(ex)}'
            )
            sys.exit(1)
        log.debug(
            f'Git repository "{self.git_server_repository_name}" created successfully'
        )

    @staticmethod
    def __transform_file(input_file_name, output_file_name, transformation):
        try:
            with open(input_file_name) as input_file:
                content = input_file.read()
                transformed_content = transformation(content)
                with open(output_file_name, "w") as output_file:
                    output_file.write(transformed_content)
        except OSError as ex:
            # TODO: fill in what/why/etc for the error message
            raise BaseVdkError(
                ErrorMessage(
                    f"Failed to transform file {input_file_name} into {output_file_name}. {str(ex)}"
                )
            )

    def __transform_template(self, content: str) -> str:
        return content.format(
            docker_registry_name=self.docker_registry_container_name,
            docker_registry_port=self.__docker_registry_port,
        )

    def __create_kind_cluster(self):
        """
        Creates a kind cluster with the private Docker registry enabled in containerd.
        """
        log.info(f'Creating Kind cluster "{self.kind_cluster_name}"...')
        with click_spinner.spinner():
            temp_file = "kind-cluster-config.yaml"
            try:
                self.__transform_file(
                    self.__current_directory.joinpath(
                        "kind-cluster-config-template.yaml"
                    ),
                    temp_file,
                    self.__transform_template,
                )
            except Exception as ex:
                log.error(
                    f'Failed to create Kind cluster "{self.kind_cluster_name}". {str(ex)}'
                )
                sys.exit(1)

            try:
                result = subprocess.run(
                    [
                        "kind",
                        "create",
                        "cluster",
                        "--config=kind-cluster-config.yaml",
                        "--name",
                        self.kind_cluster_name,
                    ],
                    capture_output=True,
                )
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                if result.returncode != 0:
                    stderr_as_str = result.stderr.decode("utf-8")
                    log.info(
                        f'Failed to create Kind cluster "{self.kind_cluster_name}". '
                        "If you have a previous installation, remove it by running `vdk server -u` and try again."
                    )
                    log.info(f"Stderr output: {stderr_as_str}")
                    sys.exit(0)
            except Exception as ex:
                log.error(
                    f'Failed to create Kind cluster "{self.kind_cluster_name}". Make sure you have Kind installed. {str(ex)}'
                )
                sys.exit(1)
        log.info(f'Kind cluster "{self.kind_cluster_name}" created')

    def __delete_kind_cluster(self):
        """
        Deletes the kind cluster.
        """
        log.info(f'Deleting Kind cluster "{self.kind_cluster_name}"...')
        try:
            result = subprocess.run(
                ["kind", "delete", "cluster", "--name", self.kind_cluster_name],
                capture_output=True,
            )
            if result.returncode != 0:
                stderr_as_str = result.stderr.decode("utf-8")
                log.error(f"Stderr output: {stderr_as_str}")
        except Exception as ex:
            log.error(
                f'Failed to delete Kind cluster "{self.kind_cluster_name}". Make sure you have Kind installed. {str(ex)}'
            )
        else:
            log.info(f'Kind cluster "{self.kind_cluster_name}" deleted successfully')

    def __get_kind_cluster(self) -> bool:
        """
        Checks whether the kind cluster exists.
        """
        try:
            result = subprocess.run(
                [
                    "kind",
                    "get",
                    "clusters",
                ],
                capture_output=True,
            )
            if result.returncode != 0:
                stderr_as_str = result.stderr.decode("utf-8")
                log.error(f"Stderr output: {stderr_as_str}")
                sys.exit(result.returncode)
            stdout_as_str = result.stdout.decode("utf-8")
            return self.kind_cluster_name in stdout_as_str.splitlines()
        except Exception as ex:
            log.error(
                f'Failed to obtain information about the Kind cluster "{self.kind_cluster_name}". '
                f"Make sure you have Kind installed. {str(ex)}"
            )
            sys.exit(1)

    def __configure_kind_local_docker_registry(self):
        """
        Documents the local registry.

        See: https://github.com/kubernetes/enhancements/tree/master/keps/sig-cluster-lifecycle/generic/1755-communicating-a-local-registry
        """
        log.debug("Configuring Kind local Docker registry...")
        config.load_kube_config()
        with client.ApiClient() as k8s_client:
            try:
                temp_file = "configmap-local-registry-hosting.yaml"
                self.__transform_file(
                    self.__current_directory.joinpath(
                        "configmap-local-registry-hosting-template.yaml"
                    ),
                    temp_file,
                    self.__transform_template,
                )
                utils.create_from_yaml(k8s_client, temp_file)
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as ex:
                log.error(f"Failed to configure local Docker registry. {str(ex)}")
                sys.exit(1)
        log.debug("Local Docker registry configured successfully")

    def __install_helm_chart(self):
        """
        Install the VDK Control Service's Helm Chart with all necessary configurations.
        """
        log.info("Installing Control Service in Kind cluster...")
        try:
            # helm repo add vdk-gitlab https://gitlab.com/api/v4/projects/28814611/packages/helm/stable
            # helm repo update
            # helm install vdk vdk-gitlab/pipelines-control-service \
            #       --set deploymentGitUrl=vdk-git-server/vdkuser/vdk-repo.git \
            #       ...
            # Note: The Git server is referenced by IP rather than directly by name; the reason for this
            # is that, currently, the Git server name cannot be resolved within the Job Builder container.
            # The reason for this is unknown, but is suspected to be related to the Kaniko image that is
            # used as a base.
            with click_spinner.spinner():
                git_server_ip = self.__resolve_container_ip(
                    self.git_server_container_name
                )
                result = subprocess.run(
                    [
                        "helm",
                        "repo",
                        "add",
                        self.helm_repo_local_name,
                        self.helm_repo_url,
                    ],
                    capture_output=True,
                )
                if result.returncode != 0:
                    stderr_as_str = result.stderr.decode("utf-8")
                    log.error(f"Stderr output: {stderr_as_str}")
                    exit(result.returncode)
                result = subprocess.run(["helm", "repo", "update"], capture_output=True)
                if result.returncode != 0:
                    stderr_as_str = result.stderr.decode("utf-8")
                    log.error(f"Stderr output: {stderr_as_str}")
                    exit(result.returncode)
                result = subprocess.run(
                    [
                        "helm",
                        "install",
                        self.helm_installation_name,
                        self.helm_chart_name,
                        "--atomic",
                        "--set",
                        "service.type=ClusterIP",
                        "--set",
                        "deploymentBuilderResourcesDefault.limits.cpu=0",
                        "--set",
                        "deploymentBuilderResourcesDefault.requests.cpu=0",
                        "--set",
                        "deploymentBuilderResourcesDefault.limits.memory=0",
                        "--set",
                        "deploymentBuilderResourcesDefault.requests.memory=0",
                        "--set",
                        "deploymentDefaultDataJobsResources.limits.cpu=0",
                        "--set",
                        "deploymentDefaultDataJobsResources.requests.cpu=0",
                        "--set",
                        "deploymentDefaultDataJobsResources.limits.memory=0",
                        "--set",
                        "deploymentDefaultDataJobsResources.requests.memory=0",
                        "--set",
                        "resources.limits.cpu=0",
                        "--set",
                        "resources.requests.cpu=0",
                        "--set",
                        "resources.limits.memory=0",
                        "--set",
                        "resources.requests.memory=0",
                        "--set",
                        "cockroachdb.statefulset.replicas=1",
                        "--set",
                        "replicas=1",
                        "--set",
                        "ingress.enabled=true",
                        "--set",
                        "deploymentGitBranch=master",
                        "--set",
                        "deploymentDockerRegistryType=generic",
                        "--set",
                        f"deploymentDockerRepository={self.docker_registry_container_name}:5000",
                        "--set",
                        "proxyRepositoryURL=localhost:5000",
                        "--set",
                        f"deploymentGitUrl={git_server_ip}/{self.git_server_admin_user}/{self.git_server_repository_name}.git",
                        "--set",
                        f"deploymentGitUsername={self.git_server_admin_user}",
                        "--set",
                        f"deploymentGitPassword={self.git_server_admin_password}",
                        "--set",
                        f"uploadGitReadWriteUsername={self.git_server_admin_user}",
                        "--set",
                        f"uploadGitReadWritePassword={self.git_server_admin_password}",
                        "--set",
                        "extraEnvVars.GIT_SSL_ENABLED=false",
                        "--set",
                        "extraEnvVars.DATAJOBS_DEPLOYMENT_BUILDER_EXTRAARGS=--insecure",
                        "--set",
                        "datajobTemplate.template.spec.successfulJobsHistoryLimit=5",
                        "--set",
                        "datajobTemplate.template.spec.failedJobsHistoryLimit=5",
                    ],
                    capture_output=True,
                )
                if result.returncode != 0:
                    stderr_as_str = result.stderr.decode("utf-8")
                    log.error(f"Stderr output: {stderr_as_str}")
                    exit(result.returncode)
                else:
                    log.info("Control Service installed successfully")
        except Exception as ex:
            log.error(
                f"Failed to install Helm chart. Make sure you have Helm installed. {str(ex)}"
            )
            sys.exit(1)

    def __uninstall_helm_chart(self):
        log.info("Uninstalling Control Service...")
        try:
            result = subprocess.run(
                ["helm", "uninstall", self.helm_installation_name], capture_output=True
            )
            if result.returncode != 0:
                stderr_as_str = result.stderr.decode("utf-8")
                log.error(f"Stderr output: {stderr_as_str}")
            else:
                log.info("Control Service uninstalled successfully")
        except Exception as ex:
            log.error(
                f"Failed to uninstall Helm chart. Make sure you have Helm installed. {str(ex)}"
            )

    def __install_ingress_prerequisites(self):
        """
        Configure an Nginx-ingress controller to forward requests from outside the cluster
        to the Control Service.

        See: https://kind.sigs.k8s.io/docs/user/ingress/#ingress-nginx
        """
        log.info("Installing prerequisites...")
        with click_spinner.spinner():
            config.load_kube_config()
            with client.ApiClient() as k8s_client:
                try:
                    utils.create_from_yaml(
                        k8s_client,
                        self.__current_directory.joinpath("ingress-nginx-deploy.yaml"),
                    )
                except Exception as ex:
                    log.error(f"Failed to install ingress controller. {str(ex)}")
                    sys.exit(1)

            # Now the Ingress is all setup, wait until is ready to process requests running:
            # kubectl wait --namespace ingress-nginx \
            #   --for=condition=ready pod \
            #   --selector=app.kubernetes.io/component=controller \
            #   --timeout=150s
            w = watch.Watch()
            k8s_client = client.CoreV1Api()
            try:
                for event in w.stream(
                    func=k8s_client.list_namespaced_pod,
                    namespace="ingress-nginx",
                    label_selector="app.kubernetes.io/component=controller",
                    timeout_seconds=180,
                ):
                    pod_status = event["object"].status
                    if pod_status.phase == "Running" and next(
                        (
                            c
                            for c in pod_status.conditions
                            if c.type == "Ready" and c.status == "True"
                        ),
                        None,
                    ):
                        break
            except Exception as ex:
                log.info(
                    f"Failed to wait for the ingress controller to start. {str(ex)}"
                )
            finally:
                w.stop()
        log.info("Done")

        # The ingress object itself is created later, as part of the Control Service's Helm chart

    @staticmethod
    def __finalize_configuration():
        log.info("Finalizing installation...")
        try:
            write_default_rest_api_url("http://localhost:8092")
        except Exception as ex:
            log.error(f"Failed to finalize installation. {str(ex)}")
            exit(1)
        log.info("Done")

    @staticmethod
    def __cleanup_configuration():
        log.info("Cleaning up...")
        try:
            reset_default_rest_api_url()
        except Exception as ex:
            log.error(f"Failed to clean up. {str(ex)}")
            exit(1)
        log.info("Done")
