# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from configparser import ConfigParser
from configparser import MissingSectionHeaderError

from vdk.internal.control.exception.vdk_exception import VDKException


log = logging.getLogger(__name__)


def read_config_ini_file(
    config_parser: ConfigParser, configuration_file_path: str
) -> None:
    """
    Read the Data Job config.ini file.

    :param config_parser: ConfigParser instance to be used for reading the
    configuration file.
    :param configuration_file_path: Path of the config.ini file
    """
    try:
        config_parser.read(configuration_file_path)
    except (MissingSectionHeaderError, Exception) as e:
        log.debug(e, exc_info=True)  # Log the traceback in DEBUG mode.
        raise VDKException(
            what="Cannot parse the Data Job configuration file"
            f" {configuration_file_path}.",
            why=f"Configuration file config.ini is probably corrupted. Error: {e}",
            consequence="Cannot deploy and configure the data job "
            "without "
            " properly set config.ini file.",
            countermeasure="config.ini must be UTF-8 compliant. "
            "Make sure the file does not contain special "
            "Unicode characters, or that your text editor "
            "has not added such characters somewhere in the file.",
        )
