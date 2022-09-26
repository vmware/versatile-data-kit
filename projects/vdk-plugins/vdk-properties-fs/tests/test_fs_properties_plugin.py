# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import shutil
import tempfile
import uuid
from configparser import ConfigParser
from unittest.mock import patch

from click.testing import Result
from vdk.plugin.properties_fs import fs_properties_plugin
from vdk.plugin.properties_fs.fs_properties_client import (
    FileSystemPropertiesServiceClient,
)
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

FS_PROPERTIES_DIRECTORY = "FS_PROPERTIES_DIRECTORY"
FS_PROPERTIES_FILENAME = "FS_PROPERTIES_FILENAME"
PROPERTIES_DEFAULT_TYPE = "PROPERTIES_DEFAULT_TYPE"

# custom directory and filename generated
directory = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
filename = str(uuid.uuid4())


@patch.dict(
    os.environ,
    {
        PROPERTIES_DEFAULT_TYPE: "fs-properties-client",
    },
)
def test_multiple_properties_read_write_config_default():
    runner = CliEntryBasedTestRunner(fs_properties_plugin)
    # default file path expected
    file_path = os.path.join(tempfile.gettempdir(), "vdk_data_jobs.properties")

    # run multiple data jobs that set matching keys and unique values
    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("write-read-properties-job")]
    )
    cli_assert_equal(0, result)
    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("write-read-properties-job-1")]
    )
    cli_assert_equal(0, result)

    config_parser = ConfigParser()
    config_parser.read(file_path)

    # verify properties stored per job
    job_section_0 = FileSystemPropertiesServiceClient._prefix(
        None, "write-read-properties-job"
    )
    job_section_1 = FileSystemPropertiesServiceClient._prefix(
        None, "write-read-properties-job-1"
    )
    assert config_parser.has_section(job_section_0)
    assert dict(config_parser.items(job_section_0)) == {
        "key": "new_value0",
        "another_key": "value0",
    }
    assert config_parser.has_section(job_section_1)
    assert dict(config_parser.items(job_section_1)) == {
        "key": "new_value1",
        "another_key": "value1",
    }


@patch.dict(
    os.environ,
    {
        PROPERTIES_DEFAULT_TYPE: "fs-properties-client",
        FS_PROPERTIES_DIRECTORY: directory,
        FS_PROPERTIES_FILENAME: filename,
    },
)
def test_properties_read_write_config_custom_directory_filename():
    runner = CliEntryBasedTestRunner(fs_properties_plugin)

    # create unique dir in temp
    os.mkdir(directory)
    try:
        file_path = os.path.join(directory, filename)
        assert not os.path.isfile(file_path)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("write-read-properties-job")]
        )
        cli_assert_equal(0, result)

        assert os.path.isfile(file_path)
    finally:
        shutil.rmtree(directory)
