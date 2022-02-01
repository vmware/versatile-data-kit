# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os

from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

KRB_AUTH = "KRB_AUTH"
KEYTAB_FOLDER = "KEYTAB_FOLDER"
KRB5_CONF_FILENAME = "KRB5_CONF_FILENAME"
KEYTAB_FILENAME = "KEYTAB_FILENAME"
KEYTAB_PRINCIPAL = "KEYTAB_PRINCIPAL"
KEYTAB_REALM = "KEYTAB_REALM"
KERBEROS_KDC_HOST = "KERBEROS_KDC_HOST"


class KerberosPluginConfiguration:
    def __init__(self, job_name: str, job_directory: str, config: Configuration):
        self.__job_name = job_name
        self.__job_directory = job_directory
        self.__config = config

    def authentication_type(self):
        return self.__config.get_value(KRB_AUTH)

    def keytab_folder(self):
        keytab_folder = self.__config.get_value(KEYTAB_FOLDER)
        if keytab_folder is None:
            keytab_folder = self.__job_directory
        return keytab_folder

    def keytab_filename(self):
        keytab_filename = self.__config.get_value(KEYTAB_FILENAME)
        if keytab_filename is None:
            keytab_filename = f"{self.__job_name}.keytab"
        return keytab_filename

    def keytab_pathname(self):
        return os.path.join(self.keytab_folder(), self.keytab_filename())

    def krb5_conf_filename(self):
        return self.__config.get_value(KRB5_CONF_FILENAME)

    def keytab_principal(self):
        keytab_principal = self.__config.get_value(KEYTAB_PRINCIPAL)
        if keytab_principal is None:
            keytab_principal = f"pa__view_{self.__job_name}"
        return keytab_principal

    def keytab_realm(self):
        return self.__config.get_value(KEYTAB_REALM)

    def kerberos_host(self):
        return self.__config.get_value(KERBEROS_KDC_HOST)


def add_definitions(config_builder: ConfigurationBuilder) -> None:
    config_builder.add(
        key=KRB_AUTH,
        default_value=None,
        description="Specifies the Kerberos authentication type to use. "
        "Possible values are 'minikerberos' and 'kinit'. "
        "If left empty, the authentication is disabled.",
    )
    config_builder.add(
        key=KEYTAB_FILENAME,
        default_value=None,
        description="Specifies the name of the keytab file. "
        "If left empty, the name of the keytab file is assumed to be the same "
        "as the name of the data job with '.keytab' suffix.",
    )
    config_builder.add(
        key=KEYTAB_FOLDER,
        default_value=None,
        description="Specifies the folder containing the keytab file. "
        "If left empty, the keytab file is expected to be located inside the data job folder.",
    )
    config_builder.add(
        key=KRB5_CONF_FILENAME,
        default_value=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "krb5.conf"
        ),
        description="Specifies the path to the krb5.conf file that should supply Kerberos configuration.",
    )
    config_builder.add(
        key=KEYTAB_PRINCIPAL,
        default_value=None,
        description="Specifies the Kerberos principal. "
        "If left empty, the principal will be the job name prepended with 'pa__view_'.",
    )
    config_builder.add(
        key=KEYTAB_REALM,
        default_value="default_realm",
        description="Specifies the Kerberos realm. This value is used only with "
        "the 'minikerberos' authentication type.",
    )
    config_builder.add(
        key=KERBEROS_KDC_HOST,
        default_value="localhost",
        description="Specifies the name of the Kerberos KDC (Key Distribution Center) host. "
        "This value is used only with the 'minikerberos' authentication type.",
    )
