# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import shutil
import tempfile
from unittest.mock import ANY
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from vdk_jupyterlab_extension.vdk_ui import RestApiUrlConfiguration
from vdk_jupyterlab_extension.vdk_ui import VdkUI


@pytest.fixture
def temp_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@patch("vdk_jupyterlab_extension.vdk_ui.clear_notebook_outputs")
@patch("vdk_jupyterlab_extension.vdk_ui.JobDeploy")
@patch("vdk_jupyterlab_extension.vdk_ui.InMemoryTextPrinter")
def test_create_deployment(
    mock_printer, mock_job_deploy, mock_clear_notebook_outputs, temp_directory
):
    path = temp_directory
    source_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "data/ingest-notebook")
    )
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(path, item)
        if os.path.isfile(source_item):
            shutil.copy2(source_item, destination_item)

    with patch.object(
        RestApiUrlConfiguration, "get_rest_api_url", return_value="http://dummy-api-url"
    ):
        mock_clear_notebook_outputs.return_value = None
        mock_cmd_instance = Mock()
        mock_job_deploy.return_value = mock_cmd_instance
        mock_printer_instance = Mock()
        mock_printer.return_value = mock_printer_instance

        mock_cmd_instance.create.return_value = None

        name = "TestJob"
        team = "TestTeam"
        reason = "Testing"

        output = VdkUI.create_deployment(name, team, path, reason)

        assert "Request to deploy job" in output
        assert "sent successfully" in output
        assert "Deployment information:" in output

        assert mock_clear_notebook_outputs.called

        mock_job_deploy.assert_called_once_with(
            "http://dummy-api-url", mock_printer_instance
        )
        mock_cmd_instance.create.assert_called_once_with(
            name=name,
            team=team,
            job_path=ANY,
            reason=reason,
            vdk_version=None,
            enabled=True,
        )


@patch("vdk_jupyterlab_extension.vdk_ui.clear_notebook_outputs")
@patch("vdk_jupyterlab_extension.vdk_ui.JobDeploy")
@patch("vdk_jupyterlab_extension.vdk_ui.InMemoryTextPrinter")
def test_create_deployment_with_invalid_path(
    mock_printer, mock_job_deploy, mock_clear_notebook_outputs, temp_directory
):
    path = "/invalid/path"
    with patch.object(
        RestApiUrlConfiguration, "get_rest_api_url", return_value="http://dummy-api-url"
    ):
        mock_clear_notebook_outputs.return_value = None
        mock_cmd_instance = Mock()
        mock_job_deploy.return_value = mock_cmd_instance
        mock_printer_instance = Mock()
        mock_printer.return_value = mock_printer_instance

        mock_cmd_instance.create.return_value = None

        name = "TestJob"
        team = "TestTeam"
        reason = "Testing"

        with pytest.raises(NotADirectoryError):
            VdkUI.create_deployment(name, team, path, reason)

        # Ensure clear_notebook_outputs and other calls were not made
        mock_clear_notebook_outputs.assert_not_called()
        mock_job_deploy.assert_not_called()
        mock_printer.assert_not_called()
        mock_cmd_instance.create.assert_not_called()
