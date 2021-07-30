# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import tempfile
from shutil import copyfile

import pytest
from taurus.vdk.control.configuration.vdk_config import VDKConfigFolder
from taurus.vdk.control.exception.vdk_exception import VDKException
from taurus.vdk.test_utils import find_test_resource


def test_save_and_delete_credentials_success():
    with tempfile.TemporaryDirectory() as dirpath:
        conf = VDKConfigFolder(dirpath)
        mock_auth_content = json.dumps(
            {
                "access_token": "axczfe12casASDCz",
                "refresh_token": "NqxjAfaxczfe12casASDCz",
                "endpoint": "http://example.com",
            }
        )
        conf.save_credentials(mock_auth_content)
        assert ".taurus.vdk" in str(os.listdir(dirpath))
        assert "vdk-cred.json" in str(os.listdir(os.path.join(dirpath, ".taurus.vdk")))
        with open(os.path.join(dirpath, ".taurus.vdk", "vdk-cred.json")) as f:
            content = f.read()
            assert mock_auth_content == content
        conf.delete_credentials()


# TODO: Check why os.chmod(dir_path, stat.S_IREAD) doesn't change permissions in the gitlab runner container
# def test_config_folder_no_permissions_error():
#    with tempfile.TemporaryDirectory() as dir_path:
#        os.chmod(dir_path, stat.S_IREAD)
#        with pytest.raises(VDKException):
#            VDKConfigFolder(dir_path)


def test_config_folder_named_file_exists_error():
    with tempfile.TemporaryDirectory() as dir_path:
        with open(os.path.join(dir_path, ".taurus.vdk"), "wb+"):
            with pytest.raises(VDKException):
                VDKConfigFolder(dir_path)


# TODO: Check why os.chmod(cred_file_mock, stat.S_IREAD) don't change permissions in the gitlab runner container
# def test_credentials_file_bad_permissions_exists_error():
#    with tempfile.TemporaryDirectory() as dir_path:
#        conf = VDKConfigFolder(dir_path)
#        mock_auth_content = json.dumps({
#            "access_token": "axczfe12casASDCz",
#            "refresh_token": "NqxjAfaxczfe12casASDCz",
#            "endpoint": "http://example.com"
#        })
#        cred_file_mock = os.path.join(dir_path, ".taurus.vdk", "vdk-cred.json")
#        with open(cred_file_mock, "w"):
#            os.chmod(cred_file_mock, stat.S_IREAD) # Fail to change permissions in gitlab runner container
#            with pytest.raises(VDKException):
#                conf.save_credentials(mock_auth_content)


def test_delete_before_save():
    with tempfile.TemporaryDirectory() as dir_path:
        conf = VDKConfigFolder(dir_path)
        conf.delete_credentials()


def test_write_configuration():
    # Setup
    test_section = "test-section"
    test_option = "test-option"
    test_value = "test-value"

    with tempfile.TemporaryDirectory() as config_dir_path:
        conf = VDKConfigFolder(config_dir_path)

        # Run
        conf.write_configuration(
            section=test_section, option=test_option, value=test_value
        )

        # Assert
        expected_config_path = os.path.join(
            conf.vdk_config_folder, VDKConfigFolder.CONFIGURATION_FILE
        )
        with open(expected_config_path) as my_file:
            actual_data = my_file.read()
            assert (
                f"[{test_section}]" and f"{test_option} = {test_value}" in actual_data
            )


def test_read_configuration():
    # Setup
    test_section = "test-section"
    test_option = "test-option"
    test_value = "test-value"
    input_test_vdk_config_path = find_test_resource("test-vdk-config")
    input_test_vdk_config_file_path = os.path.join(
        input_test_vdk_config_path, VDKConfigFolder.CONFIGURATION_FILE
    )
    assert os.path.exists(input_test_vdk_config_file_path)

    with tempfile.TemporaryDirectory() as config_dir_path:
        conf = VDKConfigFolder(config_dir_path)
        expected_config_path = os.path.join(
            conf.vdk_config_folder, VDKConfigFolder.CONFIGURATION_FILE
        )
        copyfile(src=input_test_vdk_config_file_path, dst=expected_config_path)
        assert os.path.exists(expected_config_path)

        # Run
        read_configuration_output = conf.read_configuration(
            section=test_section, option=test_option
        )

        # Assert
        assert test_value == read_configuration_output


def test_reset_configuration():
    # Setup
    test_section = "test-section"
    test_option = "test-option"
    test_value = "test-value"
    input_test_vdk_config_path = find_test_resource("test-vdk-config")
    input_test_vdk_config_file_path = os.path.join(
        input_test_vdk_config_path, VDKConfigFolder.CONFIGURATION_FILE
    )
    assert os.path.exists(input_test_vdk_config_file_path)

    with tempfile.TemporaryDirectory() as config_dir_path:
        conf = VDKConfigFolder(config_dir_path)
        expected_config_path = os.path.join(
            conf.vdk_config_folder, VDKConfigFolder.CONFIGURATION_FILE
        )
        copyfile(src=input_test_vdk_config_file_path, dst=expected_config_path)
        assert os.path.exists(expected_config_path)

        # Run
        conf.reset_configuration(section=test_section, option=test_option)

        # Assert
        with open(expected_config_path) as my_file:
            actual_data = my_file.read()
            assert f"[{test_section}]" in actual_data
            assert f"{test_option} = {test_value}" not in actual_data
