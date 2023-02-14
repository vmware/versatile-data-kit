# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib
from pathlib import Path
from typing import Optional

from vdk.plugin.control_api_auth.auth_exception import VDKAuthOSError

log = logging.getLogger(__name__)


class AuthConfig:
    @property
    def api_token_authorization_url(self) -> str:
        """
        Location of the API Token OAuth2 provider. Same as login --api-token-authorization-server-url
        This is used as default.
        """
        return os.getenv("VDK_API_TOKEN_AUTHORIZATION_URL", None)

    @property
    def api_token(self) -> str:
        """
        API Token for the OAuth2 provider used in exchange for Access Token
        Same as login --api-token.
        This is used as default.
        """
        return os.getenv("VDK_API_TOKEN", None)

    @property
    def local_config_folder(self) -> str:
        """
        Keeps local configuration of Control CLI like cached tokens, authorization uris, etc.

        Solves following use-cases:

        One scenario where two different users would like to be able to log in on the same machine.
        People sometimes share a development environment as well. Concrete example is two different user
        using the same Jenkins machine

        Also, another use-case is if you want to connect to two different Control Services with different authentication.
        For example, during development, a Demo Control Service works with staging provider but in the
        deployment in production works with Production. So in order to switch you need to re-login every time.
        But now you can just switch tabs (with different environment variables set)
        :return:
        """
        return os.getenv("VDK_BASE_CONFIG_FOLDER", str(Path.home()))


class InMemAuthConfiguration:
    """
    A class providing the equivalent of an in-memory AuthConfigFolder.
    This configuration is available as long as the python process is running,
    and is lost when the process is terminated.
    """

    CREDS_KEY = "credentials"

    def __init__(self):
        self._config = dict()

    def save_credentials(self, content: str) -> None:
        self._config[InMemAuthConfiguration.CREDS_KEY] = content

    def delete_credentials(self) -> None:
        self._config[InMemAuthConfiguration.CREDS_KEY] = ""

    def read_credentials(self) -> Optional[str]:
        return self._config.get(InMemAuthConfiguration.CREDS_KEY)


class AuthConfigFolder:
    """
    A class responsible for managing the configuration files in the vdk configuration
    folder
    """

    # TODO: this looks robust: https://github.com/ActiveState/appdirs
    CONFIG_FOLDER_NAME = ".vdk.internal"
    CREDENTIALS_FILE = "vdk-cred.json"
    CONFIGURATION_FILE = "vdk-configuration.ini"

    def __init__(self, base_dir=AuthConfig().local_config_folder):
        self.vdk_config_folder = os.path.join(
            base_dir, AuthConfigFolder.CONFIG_FOLDER_NAME
        )
        if os.path.isfile(self.vdk_config_folder):
            raise VDKAuthOSError(
                what="Credentials file was not created",
                why=f"There is a file named {self.vdk_config_folder}",
                consequence="User won't be able to access Control Service",
                countermeasure=f"Remove file {self.vdk_config_folder}",
            )
        else:
            if not os.path.exists(self.vdk_config_folder) and not os.path.isdir(
                self.vdk_config_folder
            ):
                try:
                    pathlib.Path(self.vdk_config_folder).mkdir(
                        parents=True, exist_ok=True
                    )
                except Exception as e:
                    raise VDKAuthOSError(
                        what="Configuration folder was not created and user is not logged in",
                        why=f"Cannot create: {self.vdk_config_folder} configuration folder: {str(e)}",
                        consequence="User won't be able to access Control Service",
                        countermeasure=f"Check if the client has write access to: {base_dir}",
                    )

    def save_credentials(self, content):
        try:
            credentials_file_path = self.__get_cred_file()
            log.debug(f"Save vdk credential file: {credentials_file_path} ")
            with open(credentials_file_path, "w+") as temp_file:
                temp_file.write(content)
        except OSError as e:
            raise VDKAuthOSError(
                what="Credentials file was not created",
                why=f"Cannot create credentials file: {str(e)}",
                consequence="User won't be able to access Control Service",
                countermeasure="Check permissions of vdk-cred.json file in .vdk folder inside home directory",
            )

    def delete_credentials(self):
        credentials_file_path = self.__get_cred_file()
        log.debug(f"Delete vdk credential file: {credentials_file_path} ...")
        if os.path.exists(credentials_file_path):
            try:
                os.remove(credentials_file_path)
            except OSError as e:
                raise VDKAuthOSError(
                    what="Credentials file was not deleted",
                    why=f"Cannot delete credentials file in .vdk folder in home directory: {str(e)}",
                    consequence="User is not logged out",
                    countermeasure="Check permissions of vdk-cred.json file in .vdk folder in home directory",
                )

    def read_credentials(self):
        try:
            credentials_file_path = self.__get_cred_file()
            log.debug(f"Reading vdk credential file: {credentials_file_path} ...")
            if os.path.isfile(credentials_file_path):
                with open(credentials_file_path) as temp_file:
                    return temp_file.read()
            return ""
        except OSError as e:
            raise VDKAuthOSError(
                what="Credentials file cannot be accessed.",
                why=f"Most likely not login. Error was: {str(e)}",
                consequence="User won't be able to authenticate against Control Service",
                countermeasure="Make sure you have executed vdk login first. ",
            )

    def __get_cred_file(self):
        return os.path.join(self.vdk_config_folder, AuthConfigFolder.CREDENTIALS_FILE)
