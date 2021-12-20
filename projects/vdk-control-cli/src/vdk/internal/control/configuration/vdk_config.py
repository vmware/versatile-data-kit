# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib
from configparser import ConfigParser
from pathlib import Path

from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.control.utils.control_utils import read_config_ini_file

log = logging.getLogger(__name__)


class VDKConfig:
    # we want the same op id for the single execution of vdk hence static variable
    import uuid

    _op_id = os.environ.get("VDK_OP_ID_OVERRIDE", f"{uuid.uuid4().hex}"[:16])

    @property
    def op_id(self) -> str:
        """
        Operational ID that is used to make easier troubleshooting and trace.

        Control Service checks header "X-OPID" and if set uses as op id printed in its
        logs and also send it to the next service (rudimentary tracing),
        op id is also persisted by vdk as system column.

        One simplistic example of how it can be used - we can see from logs of
        vdk the op id (fa89cca9c6f146cd)
        `2021-02-14 10:15:21,97710.0 [DEBUG] vdk.internal vdk_config:88
        read_credentials[OpId:fa89cca9c6f146cd]- Reading vdk credential ...`

        And then we can search in logs of control service
        kubectl logs pod/control-service-dep-6548b85c55-xkz8p | grep fa89cca9c6f146cd

        """
        return VDKConfig._op_id

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

    @property
    def control_service_rest_api_url(self) -> str:
        return os.getenv("VDK_CONTROL_SERVICE_REST_API_URL", None)

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
        Same as loign --api-token.
        This is used as default.
        """
        return os.getenv("VDK_API_TOKEN", None)

    @property
    def http_connect_timeout_seconds(self) -> int:
        return int(os.getenv("VDK_CONTROL_HTTP_CONNECT_TIMEOUT_SECONDS", "30"))

    @property
    def http_connect_retries(self) -> int:
        return int(os.getenv("VDK_CONTROL_HTTP_CONNECT_RETRIES", "6"))

    @property
    def http_read_timeout_seconds(self) -> int:
        return int(os.getenv("VDK_CONTROL_HTTP_READ_TIMEOUT_SECONDS", "900"))

    @property
    def http_read_retries(self) -> int:
        return int(os.getenv("VDK_CONTROL_HTTP_READ_RETRIES", "6"))

    @property
    def http_total_retries(self) -> int:
        return int(os.getenv("VDK_CONTROL_HTTP_TOTAL_RETRIES", "10"))

    @property
    def http_connection_pool_maxsize(self) -> int:
        return int(os.getenv("VDK_CONTROL_HTTP_CONNECTION_POOL_MAXSIZE", "2"))

    @property
    def http_verify_ssl(self) -> bool:
        return os.getenv("VDK_CONTROL_HTTP_VERIFY_SSL", "True").lower() in (
            "true",
            "1",
            "t",
        )

    @property
    def sample_job_directory(self) -> str:
        sample_job_dir = os.getenv("VDK_CONTROL_SAMPLE_JOB_DIRECTORY", None)
        if not sample_job_dir:
            import vdk.internal.control.job.sample_job

            template_module_path = vdk.internal.control.job.sample_job.__path__._path[0]
            sample_job_dir = os.path.abspath(template_module_path)
        return sample_job_dir


class VDKConfigFolder:
    """
    A class responsible for managing the configuration files in the vdk configuration
    folder
    """

    # TODO: this looks robust: https://github.com/ActiveState/appdirs
    CONFIG_FOLDER_NAME = ".vdk.internal"
    CREDENTIALS_FILE = "vdk-cred.json"
    CONFIGURATION_FILE = "vdk-configuration.ini"

    def __init__(self, base_dir=VDKConfig().local_config_folder):
        self.vdk_config_folder = os.path.join(
            base_dir, VDKConfigFolder.CONFIG_FOLDER_NAME
        )
        if os.path.isfile(self.vdk_config_folder):
            raise VDKException(
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
                    raise VDKException(
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
            raise VDKException(
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
                raise VDKException(
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
            raise VDKException(
                what="Credentials file cannot be accessed.",
                why=f"Most likely not login. Error was: {str(e)}",
                consequence="User won't be able to authenticate against Control Service",
                countermeasure="Make sure you have executed vdk login first. ",
            )

    def read_configuration(self, section, option, fallback=None):
        try:
            configuration_file_path = self.__get_configuration_file()
            log.debug(f"Reading configuration file: {configuration_file_path} ...")

            config_parser = ConfigParser()

            read_config_ini_file(
                config_parser=config_parser,
                configuration_file_path=configuration_file_path,
            )

            return config_parser.get(section=section, option=option, fallback=fallback)
        except OSError as e:
            raise VDKException(
                what="Configuration file cannot be accessed.",
                why=f"Configuration file is not accessible. Error was: {str(e)}",
                consequence="User won't be able to use configurations like predefined default team name, etc.",
                countermeasure="Make sure the configuration file is accessible for the user running the tool.",
            )

    def write_configuration(self, section, option, value):
        try:
            configuration_file_path = self.__get_configuration_file()
            log.debug(
                f"Writing to the configuration file: {configuration_file_path} ..."
            )

            config_parser = ConfigParser()
            config_parser.read(configuration_file_path)

            if value is None:
                self.reset_value(
                    config_parser=config_parser, section=section, option=option
                )
            else:
                self.set_value(
                    config_parser=config_parser,
                    section=section,
                    option=option,
                    value=value,
                )
            with open(configuration_file_path, "w") as config_file:
                config_parser.write(config_file)

        except OSError as e:
            raise VDKException(
                what="Configuration file cannot be accessed.",
                why=f"Configuration file is not accessible. Error was: {str(e)}",
                consequence="User won't be able to save configurations like predefined default team name, etc.",
                countermeasure="Make sure the configuration file is accessible for the user running the tool.",
            )

    def reset_configuration(self, section, option):
        self.write_configuration(section=section, option=option, value=None)

    @staticmethod
    def reset_value(config_parser, section, option):
        if config_parser.has_option(section=section, option=option):
            log.debug(f"Removing option {option} from section {section} ...")
            config_parser.remove_option(section=section, option=option)

    @staticmethod
    def set_value(config_parser, section, option, value):
        log.debug(f"Setting value for option {option} in section {section} ...")

        if not config_parser.has_section(section):
            config_parser.add_section(section)

        config_parser.set(section=section, option=option, value=value)

    def __get_cred_file(self):
        return os.path.join(self.vdk_config_folder, VDKConfigFolder.CREDENTIALS_FILE)

    def __get_configuration_file(self):
        return os.path.join(self.vdk_config_folder, VDKConfigFolder.CONFIGURATION_FILE)
