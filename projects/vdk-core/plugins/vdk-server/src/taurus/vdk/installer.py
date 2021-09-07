import base64
import time

import docker
import logging
import os
import pathlib
import subprocess
import sys
import requests
from kubernetes import client, config, utils
from taurus.vdk.core.errors import BaseVdkError, ErrorMessage

log = logging.getLogger(__name__)


class Installer(object):
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
        self.__current_directory = self.get_current_directory()

    def install(self):
        """
        Installs all necessary components and configurations.
        """
        log.info(f"Starting installation of Versatile Data Kit Control Service")
        self.__create_docker_registry_container()
        if self.__create_git_server_container():
            self.__configure_git_server_with_error_handling()
            self.__create_git_repository()
            self.__restart_git_server_container()
        self.__create_kind_cluster()
        self.__connect_container_to_kind_network(self.docker_registry_container_name)
        self.__connect_container_to_kind_network(self.git_server_container_name)
        self.__git_server_ip = self.__resolve_container_ip(self.git_server_container_name)
        self.__configure_kind_local_docker_registry()
        self.__install_helm_chart()
        log.info(f"Versatile Data Kit Control Service installed successfully")

    def uninstall(self):
        """
        Uninstalls all components.
        """
        self.__uninstall_helm_chart()
        self.__delete_kind_cluster()
        self.__delete_git_server_container()
        self.__delete_docker_registry_container()

    @staticmethod
    def get_current_directory() -> pathlib.Path:
        return pathlib.Path(__file__).parent.resolve()

    def __create_docker_registry_container(self):
        """
        Creates a Docker registry container with name specified by docker_registry_name,
        unless a container with this name already exists.
        """
        docker_client = docker.from_env()
        try:
            # Check if a container with that name already exists by inspecting it;
            # If the inspection throws an exception, the container does not exist and we
            # proceed with creating it
            docker_client.api.inspect_container(self.docker_registry_container_name)
        except:
            try:
                # docker run -d --restart=always -p "127.0.0.1:${docker_registry_port}:5000" --name "${docker_registry_name}" registry:2
                docker_client.containers.run("registry:2",
                                      detach=True,
                                      restart_policy={"Name": "always"},
                                      name=self.docker_registry_container_name,
                                      ports={'5000/tcp': ('127.0.0.1', self.__docker_registry_port)})
            except Exception as ex:
                log.error(
                    f"Error: Failed to create Docker registry container {self.docker_registry_container_name}. {str(ex)}")
        finally:
            docker_client.close()

    def __delete_docker_registry_container(self):
        self.__delete_container(self.docker_registry_container_name)

    @staticmethod
    def __delete_container(container_name: str):
        """
        Deletes the Docker registry container with the specified name.
        """
        docker_client = docker.from_env()
        try:
            docker_client.api.inspect_container(container_name)
            docker_client.api.stop(container_name)
            docker_client.api.remove_container(container_name)
        except Exception as ex:
            log.error(f"Error: Failed to remove Docker container {container_name}. {str(ex)}")
        finally:
            docker_client.close()

    def __restart_git_server_container(self):
        self.__restart_container(self.git_server_container_name)

    @staticmethod
    def __restart_container(container_name: str):
        """
        Restarts the container with the specified name.
        """
        docker_client = docker.from_env()
        try:
            docker_client.api.inspect_container(container_name)
            docker_client.api.restart(container_name)
        except Exception as ex:
            log.info(f"Failed to restart Docker container {container_name}. {str(ex)}")
        finally:
            docker_client.close()

    def __create_git_server_container(self) -> bool:
        """
        Creates a Git server container with name specified by docker_registry_name,
        unless a container with this name already exists.

        Returns true if the container did not exist and was created successfully; otherwise, false.
        """
        docker_client = docker.from_env()
        try:
            # Check if a container with that name already exists by inspecting it;
            # If the inspection throws an exception, the container does not exist and we
            # proceed with creating it
            docker_client.api.inspect_container(self.git_server_container_name)
            return False
        except:
            try:
                # docker run --name=vdk-git-server -p 10022:22 -p 10080:3000 -p 10081:80 gogs/gogs:0.12
                docker_client.containers.run("gogs/gogs:0.12",
                                      detach=True,
                                      name=self.git_server_container_name,
                                      ports={'22/tcp': '10022', '3000/tcp': '10080', '80/tcp': '10081'})
                return True
            except Exception as ex:
                log.error(f"Error: Failed to create Git server container {self.git_server_container_name}. {str(ex)}")
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
        docker_client = docker.from_env()
        try:
            # docker network connect "kind" "{container_name}"
            docker_client.api.connect_container_to_network(container_name, "kind")
        except Exception as ex:
            log.info(ex)
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
            kind_network = next((n for n in networks if n['Name'] == 'kind'), None)
            # Find the "kind" network configuration
            # docker network inspect "{kind_net_id}"
            kind_network_details = docker_client.api.inspect_network(kind_network['Id'])
            # Extract the container's IP
            containers = kind_network_details['Containers']
            container_id = next((c for c in containers if containers[c]['Name'] == container_name), None)
            if container_id:
                return self.__remove_ip_subnet_mask(containers[container_id]['IPv4Address'])
        except Exception as ex:
            log.info(ex)
        finally:
            docker_client.close()

    @staticmethod
    def __remove_ip_subnet_mask(ip: str) -> str:
        pos = ip.find('/')
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
        attempt = 1
        max_attempts = 5
        while attempt <= max_attempts:
            try:
                self.__configure_git_server()
            except Exception as ex:
                ex_as_string = str(ex)
                if "Connection reset by peer" in ex_as_string:
                    log.debug(f"Failed to configure git server. Will reattempt in 2 seconds...")
                    attempt += 1
                    time.sleep(2)
                    continue
                if "/user/login" not in ex_as_string:
                    log.error(f"Error: Failed to configure git server. {ex_as_string}")
                    sys.exit(1)
                break

    def __configure_git_server(self):
        """
        Configures the Git server at localhost:10080 with the configurations
        specified by the git_server_* variables.
        """
        # curl -X POST 'http://localhost:10080/install'  \
        # -d "db_type=SQLite3&db_path=data/gogs.db&app_name=Gogs&repo_root_path=/data/git/gogs-repositories&run_user=git&domain=localhost&ssh_port=22&http_port=80&app_url=http://localhost/&log_root_path=/app/gogs/log&smtp_host=&smtp_from=&smtp_user=&smtp_passwd=&disable_gravatar=true&enable_captcha=false&register_confirm=false&admin_name=vdkuser&admin_passwd=vdkpass&admin_confirm_passwd=vdkpass&admin_email=vdk_user@vmware.com"
        requests.post("http://localhost:10080/install",
                      data={
                          'db_type': 'SQLite3',
                          'db_path': 'data/gogs.db',
                          'app_name': 'Gogs',
                          'repo_root_path': '/data/git/gogs-repositories',
                          'run_user': 'git',
                          'domain': 'localhost',
                          'ssh_port': 22,
                          'http_port': 80,
                          'app_url': 'http://localhost/',
                          'log_root_path': '/app/gogs/log',
                          'smtp_host': '',
                          'smtp_from': '',
                          'smtp_user': '',
                          'smtp_passwd': '',
                          'disable_gravatar': 'true',
                          'enable_captcha': 'false',
                          'register_confirm': 'false',
                          'admin_name': self.git_server_admin_user,
                          'admin_passwd': self.git_server_admin_password,
                          'admin_confirm_passwd': self.git_server_admin_password,
                          'admin_email': self.git_server_admin_email
                      })

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
        try:
            credentials = f"{self.git_server_admin_user}:{self.git_server_admin_password}"
            base64_credentials = base64.b64encode(credentials.encode("ascii")).decode("ascii")
            requests.post(f"http://localhost:10080/api/v1/admin/users/{self.git_server_admin_user}/repos",
                          headers={
                              'authorization': f'Basic {base64_credentials}',
                              'content-type': 'application/json'
                          },
                          json={
                              'name': self.git_server_repository_name,
                              'description': 'A repository for storing the source code of VDK data jobs',
                              'private': False
                          })
        except Exception as ex:
            log.error(f"Error: Failed to create git repository. {str(ex)}")
            sys.exit(1)

    @staticmethod
    def __transform_file(input_file_name, output_file_name, transformation):
        try:
            with open(input_file_name, "r") as input_file:
                content = input_file.read()
                transformed_content = transformation(content)
                with open(output_file_name, "w") as output_file:
                    output_file.write(transformed_content)
        except IOError as ex:
            # TODO: fill in what/why/etc for the error message
            raise BaseVdkError(
                ErrorMessage(f"Failed to transform file {input_file_name} into {output_file_name}. {str(ex)}"))

    def __transform_template(self, content: str) -> str:
        return content.format(docker_registry_name=self.docker_registry_container_name,
                              docker_registry_port=self.__docker_registry_port)

    def __create_kind_cluster(self):
        """
        Creates a kind cluster with the private Docker registry enabled in containerd.
        """
        temp_file = "kind-cluster-config.yaml"
        try:
            self.__transform_file(self.__current_directory.joinpath("kind-cluster-config-template.yaml"),
                                  temp_file,
                                  self.__transform_template)
        except Exception as ex:
            log.error(f"Failed to create Kind cluster. {str(ex)}")
            exit(1)

        try:
            completed_process = subprocess.run(["kind", "create", "cluster",
                                                "--config=kind-cluster-config.yaml",
                                                "--name", self.kind_cluster_name])
            if os.path.exists(temp_file):
                os.remove(temp_file)
            if completed_process.returncode == 1:
                sys.exit(1)
        except Exception as ex:
            log.error(f"Failed to create Kind cluster. Make sure you have Kind installed. {str(ex)}")

    def __delete_kind_cluster(self):
        """
        Deletes the kind cluster.
        """
        try:
            completed_process = subprocess.run(["kind", "delete", "cluster",
                                                "--name", self.kind_cluster_name])
            if completed_process.returncode == 1:
                sys.exit(1)
        except Exception as ex:
            log.error(f"Failed to delete Kind cluster. Make sure you have Kind installed. {str(ex)}")

    def __configure_kind_local_docker_registry(self):
        """
        Documents the local registry.

        See: https://github.com/kubernetes/enhancements/tree/master/keps/sig-cluster-lifecycle/generic/1755-communicating-a-local-registry
        """
        config.load_kube_config()
        with client.ApiClient() as k8s_client:
            try:
                temp_file = "configmap-local-registry-hosting.yaml"
                self.__transform_file(
                    self.__current_directory.joinpath("configmap-local-registry-hosting-template.yaml"),
                    temp_file,
                    self.__transform_template)
                utils.create_from_yaml(k8s_client, temp_file)
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as ex:
                log.info(ex)

    def __install_helm_chart(self):
        """
        Install the VDK Control Service's Helm Chart with all necessary configurations.
        """
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
            subprocess.run(['helm', 'repo', 'add', self.helm_repo_local_name, self.helm_repo_url])
            subprocess.run(['helm', 'repo', 'update'])
            subprocess.run(['helm', 'install', self.helm_installation_name, self.helm_chart_name,
                            # '--wait',
                            # '--debug',
                            '--set', 'resources.limits.memory=1G',
                            '--set', 'cockroachdb.statefulset.replicas=1',
                            '--set', 'replicas=1',
                            '--set', 'deploymentBuilderImage.tag=1.2', # TODO: Remove when service adopts 1.2
                            '--set', 'deploymentGitBranch=master',
                            '--set', 'deploymentDockerRegistryType=generic',
                            '--set', f'deploymentDockerRepository={self.docker_registry_container_name}:5000',
                            '--set', f'proxyRepositoryURL=localhost:5000',
                            '--set', f'deploymentGitUrl={self.__git_server_ip}/{self.git_server_admin_user}/{self.git_server_repository_name}.git',
                            '--set', f'deploymentGitUsername={self.git_server_admin_user}',
                            '--set', f'deploymentGitPassword={self.git_server_admin_password}',
                            '--set', f'uploadGitReadWriteUsername={self.git_server_admin_user}',
                            '--set', f'uploadGitReadWritePassword={self.git_server_admin_password}',
                            '--set', 'extraEnvVars.GIT_SSL_ENABLED=false',
                            '--set', 'extraEnvVars.DATAJOBS_DEPLOYMENT_BUILDER_EXTRAARGS=--insecure',
                            ])
        except Exception as ex:
            log.error(f"Failed to install Helm chart. Make sure you have Helm installed. {str(ex)}")

    def __uninstall_helm_chart(self):
        try:
            subprocess.run(["helm", "uninstall", self.helm_installation_name])
        except Exception as ex:
            log.error(f"Failed to uninstall Helm chart. Make sure you have Helm installed. {str(ex)}")
