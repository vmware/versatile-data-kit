import base64
import docker
import logging
import os
import subprocess
import sys
import requests
from kubernetes import client, config, utils


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
    docker_registry_port = 5000
    helm_installation_name = "vdk"
    helm_repo_url = "https://gitlab.com/api/v4/projects/28814611/packages/helm/stable"
    helm_chart_name = "vdk-gitlab/pipelines-control-service"
    helm_repo_local_name = "vdk-gitlab"
    git_server_container_name = "vdk-git-server"
    git_server_admin_user = "vdkuser"
    git_server_admin_password = "vdkpass"
    git_server_admin_email = "vdkuser@vmware.com"
    git_server_repository_name = "vdk-git-repo"


    def install(self):
        """
        Installs all necessary components and configurations.
        """
        self.__create_docker_registry_container()
        if self.__create_git_server_container():
            self.__configure_git_server()
            self.__create_git_repository()
            self.__restart_git_server_container()
        self.__create_kind_cluster()
        self.__connect_container_to_kind_network(self.docker_registry_container_name)
        self.__connect_container_to_kind_network(self.git_server_container_name)
        self.__configure_kind_local_docker_registry()
        self.__install_helm_chart()

    def uninstall(self):
        """
        Uninstalls all components.
        """
        self.__uninstall_helm_chart()
        self.__delete_kind_cluster()
        self.__delete_git_server_container()
        self.__delete_docker_registry_container()

    def __create_docker_registry_container(self):
        """
        Creates a Docker registry container with name specified by docker_registry_name,
        unless a container with this name already exists.
        """
        client = docker.from_env()
        try:
            # Check if a container with that name already exists by inspecting it;
            # If the inspection throws an exception, the container does not exist and we
            # proceed with creating it
            client.api.inspect_container(self.docker_registry_container_name)
        except:
            try:
                # docker run -d --restart=always -p "127.0.0.1:${docker_registry_port}:5000" --name "${docker_registry_name}" registry:2
                client.containers.run("registry:2",
                                       detach=True,
                                       restart_policy={"Name": "always"},
                                       name=self.docker_registry_container_name,
                                       ports={'5000/tcp': ('127.0.0.1', self.docker_registry_port)})
            except Exception as ex:
                log.error(f"Error: Failed to create Docker registry container {self.docker_registry_container_name}. {str(ex)}")
        finally:
            client.close

    def __delete_docker_registry_container(self):
        self.__delete_container(self.docker_registry_container_name)

    def __delete_container(self, container_name: str):
        """
        Deletes the Docker registry container with the specified name.
        """
        client = docker.from_env()
        try:
            client.api.inspect_container(container_name)
            client.api.stop(container_name)
            client.api.remove_container(container_name)
        except Exception as ex:
            log.error(f"Error: Failed to remove Docker container {container_name}. {str(ex)}")
        finally:
            client.close

    def __restart_git_server_container(self):
        self.__restart_container(self.git_server_container_name)

    def __restart_container(self, container_name: str):
        """
        Restarts the container with the specified name.
        """
        client = docker.from_env()
        try:
            client.api.inspect_container(container_name)
            client.api.restart(container_name)
        except Exception as ex:
            log.info(f"Failed to restart Docker container {container_name}. {str(ex)}")
        finally:
            client.close

    def __create_git_server_container(self) -> bool:
        """
        Creates a Git server container with name specified by docker_registry_name,
        unless a container with this name already exists.

        Returns true if the container did not exist and was created successfully; otherwise, false.
        """
        client = docker.from_env()
        try:
            # Check if a container with that name already exists by inspecting it;
            # If the inspection throws an exception, the container does not exist and we
            # proceed with creating it
            client.api.inspect_container(self.git_server_container_name)
            return False
        except:
            try:
                # docker run --name=vdk-git-server -p 10022:22 -p 10080:3000 -p 10081:80 gogs/gogs:0.12
                client.containers.run("gogs/gogs:0.12",
                                       detach=True,
                                       name=self.git_server_container_name,
                                       ports={'22/tcp': '10022', '3000/tcp': '10080', '80/tcp': '10081'})
                return True
            except Exception as ex:
                log.error(f"Error: Failed to create Git server container {self.git_server_container_name}. {str(ex)}")
        finally:
            client.close

    def __delete_git_server_container(self):
        self.__delete_container(self.git_server_container_name)

    def __connect_container_to_kind_network(self, container_name: str):
        """
        Connects a Docker container to the Kind cluster network.
        If the container is already connected, an info message is logged.
        """
        client = docker.from_env()
        try:
            client.api.connect_container_to_network(container_name, "kind")
        except Exception as ex:
            log.info(ex)
        finally:
            client.close

    def __configure_git_server(self):
        """
        Configures the Git server at localhost:10080 with the configurations
        specified by the git_server_* variables.
        """
        # curl -X POST 'http://localhost:10080/install'  \
        # -d "db_type=SQLite3&db_path=data/gogs.db&app_name=Gogs&repo_root_path=/data/git/gogs-repositories&run_user=git&domain=localhost&ssh_port=22&http_port=80&app_url=http://localhost/&log_root_path=/app/gogs/log&smtp_host=&smtp_from=&smtp_user=&smtp_passwd=&disable_gravatar=true&enable_captcha=false&register_confirm=false&admin_name=vdkuser&admin_passwd=vdkpass&admin_confirm_passwd=vdkpass&admin_email=vdk_user@vmware.com"
        try:
            requests.post("http://localhost:10080/install",
                          params={
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
        except Exception as ex:
            log.error(f"Error: Failed to configure git server. {str(ex)}")
            sys.exit(1)

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
            base64_credentials = base64.b64encode(credentials.encode("ascii"))
            requests.post(f"http://localhost:10080/api/v1/admin/users/{self.git_server_admin_user}/repos",
                          headers={
                              'authorization': f'Basic {base64_credentials}',
                              'content-type': 'application/json'
                          },
                          data={
                              'name': self.git_server_repository_name,
                              'description': 'This is a VDK repository for storing the source code of data jobs',
                              'private': 'false'
                          })
        except Exception as ex:
            log.error(f"Error: Failed to create git repository. {str(ex)}")
            sys.exit(1)


    def __transform_file(self, input_file_name, output_file_name, transformation):
        try:
            with open(input_file_name, "r") as input_file:
                content = input_file.read()
                transformed_content = transformation(content)
                with open(output_file_name, "w") as output_file:
                    output_file.write(transformed_content)
        except IOError as ex:
            log.error(f"Error: Failed to transform file {input_file_name} into {output_file_name}. {str(ex)}")

    def __transform_template(self, content: str) -> str:
        return content.format(docker_registry_name = self.docker_registry_container_name,
                              docker_registry_port = self.docker_registry_port)

    def __create_kind_cluster(self):
        """
        Creates a kind cluster with the private Docker registry enabled in containerd.
        """
        self.__transform_file("kind-cluster-config-template.yaml",
                              "kind-cluster-config.yaml",
                              self.__transform_template)
        try:
            completed_process = subprocess.run(["kind", "create", "cluster",
                                               "--config=kind-cluster-config.yaml",
                                               "--name", self.kind_cluster_name])
            if os.path.exists("kind-cluster-config.yaml"):
                os.remove("kind-cluster-config.yaml")
            if completed_process.returncode == 1:
                sys.exit(1)
        except Exception as ex:
            log.error(f"Error: Failed to create Kind cluster. Make sure you have Kind installed. {str(ex)}")

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
            log.error(f"Error: Failed to delete Kind cluster. Make sure you have Kind installed. {str(ex)}")

    def __configure_kind_local_docker_registry(self):
        """
        Documents the local registry.

        See: https://github.com/kubernetes/enhancements/tree/master/keps/sig-cluster-lifecycle/generic/1755-communicating-a-local-registry
        """
        config.load_kube_config()
        with client.ApiClient() as k8s_client:
            try:
                self.__transform_file("configmap-local-registry-hosting-template.yaml",
                                      "configmap-local-registry-hosting.yaml",
                                      self.__transform_template)
                utils.create_from_yaml(
                    k8s_client, "configmap-local-registry-hosting.yaml")
                if os.path.exists("configmap-local-registry-hosting.yaml"):
                    os.remove("configmap-local-registry-hosting.yaml")
            except Exception as ex:
                log.info(ex)

    def __install_helm_chart(self):
        try:
            # helm repo add vdk-gitlab https://gitlab.com/api/v4/projects/28814611/packages/helm/stable
            # helm repo update
            # helm install my-release vdk-gitlab/pipelines-control-service
            subprocess.run(["helm", "repo", "add", self.helm_repo_local_name, self.helm_repo_url])
            subprocess.run(["helm", "repo", "update"])
            subprocess.run(["helm", "install", self.helm_installation_name, self.helm_chart_name])
        except Exception as ex:
            log.error(f"Error: Failed to install Helm chart. Make sure you have Helm installed. {str(ex)}")

    def __uninstall_helm_chart(self):
        try:
            subprocess.run(["helm", "uninstall", self.helm_installation_name])
        except Exception as ex:
            log.error(f"Error: Failed to uninstall Helm chart. Make sure you have Helm installed. {str(ex)}")

