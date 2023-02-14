# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import tempfile
from unittest import mock

import pytest
from vdk.internal.heartbeat.config import Config


@mock.patch.dict(
    os.environ,
    {
        "VDKCLI_OAUTH2_REFRESH_TOKEN": "some-test-token",
    },
)
def test_get_atleast_one_value_from_env_vars():
    config = Config()

    # Both variables set
    with mock.patch.dict(
        os.environ,
        {
            "VAR1": "value1",
            "VAR2": "value2",
        },
    ):
        assert "value1" == config._get_atleast_one_value("VAR1", "VAR2")

    # Only first variable set
    with mock.patch.dict(
        os.environ,
        {
            "VAR1": "value1",
        },
    ):
        assert "value1" == config._get_atleast_one_value("VAR1", "VAR2")

    # Only second variable set
    with mock.patch.dict(
        os.environ,
        {
            "VAR2": "value2",
        },
    ):
        assert "value2" == config._get_atleast_one_value("VAR1", "VAR2")

    # No value and exception
    with pytest.raises(Exception):
        config._get_atleast_one_value("VAR1", "VAR2")

    # No value and no exception
    assert not config._get_atleast_one_value("VAR1", "VAR2", is_required=False)


@mock.patch.dict(
    os.environ,
    {
        "VDKCLI_OAUTH2_REFRESH_TOKEN": "some-test-token",
    },
)
def test_get_atleast_one_value_from_config_ini():
    config_ini_path = os.path.join(str(tempfile.gettempdir()), "config.ini")
    with open(config_ini_path, "w") as text_file:
        text_file.write(
            """
        [DEFAULT]
            VAR1=False
            VAR2=None
            VAR3=
            VAR4=valid_value
        """
        )

    config = Config(config_ini_path)

    # Set var to False
    assert "False" == config._get_atleast_one_value("VAR1", "VAR2")

    # Set var to None
    assert "None" == config._get_atleast_one_value("VAR2", "VAR3")

    # Set var to empty string
    assert "" == config._get_atleast_one_value("VAR3", "VAR4")

    # Set var to valid string
    assert "valid_value" == config._get_atleast_one_value("VAR4", "VAR5")

    # No value and exception
    with pytest.raises(Exception):
        config._get_atleast_one_value("VAR5", "VAR6")

    # No value and no exception
    assert not config._get_atleast_one_value("VAR5", "VAR6", is_required=False)
