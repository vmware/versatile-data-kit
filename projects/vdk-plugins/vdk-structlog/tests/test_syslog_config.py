# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging.handlers
import socket
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from vdk.plugin.structlog.filters import AttributeAdder
from vdk.plugin.structlog.syslog_config import configure_syslog_handler
from vdk.plugin.structlog.syslog_config import DETAILED_FORMAT


@pytest.fixture
def mock_job_context():
    job_context = MagicMock()
    job_context.name = "test_job"
    job_context.core_context.state.get.return_value = "12345"
    job_context.core_context.configuration.get_value.side_effect = lambda key: {
        "SYSLOG_ENABLED": True,
        "SYSLOG_HOST": "localhost",
        "SYSLOG_PORT": 514,
        "SYSLOG_PROTOCOL": "UDP",
    }.get(key, None)
    return job_context


def test_configure_syslog_handler_enabled(mock_job_context):
    syslog_handler = configure_syslog_handler(
        mock_job_context.core_context.configuration.get_value("SYSLOG_ENABLED"),
        mock_job_context.core_context.configuration.get_value("SYSLOG_HOST"),
        mock_job_context.core_context.configuration.get_value("SYSLOG_PORT"),
        mock_job_context.core_context.configuration.get_value("SYSLOG_PROTOCOL"),
        mock_job_context.name,
        mock_job_context.core_context.state.get(),
    )
    assert isinstance(syslog_handler, logging.handlers.SysLogHandler)
    assert syslog_handler.level == logging.DEBUG
    assert any(isinstance(filter, AttributeAdder) for filter in syslog_handler.filters)
    assert syslog_handler.formatter._fmt == DETAILED_FORMAT


@pytest.mark.parametrize("protocol", ["UDP", "TCP"])
@patch("socket.socket")
def test_configure_syslog_handler_with_different_protocols(
    mock_socket, protocol, mock_job_context
):
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance

    syslog_handler = configure_syslog_handler(
        True,
        "localhost",
        514,
        protocol,
        mock_job_context.name,
        mock_job_context.core_context.state.get(),
    )

    expected_socktype = socket.SOCK_DGRAM if protocol == "UDP" else socket.SOCK_STREAM
    assert mock_socket.called
    assert mock_socket.call_args[0][1] == expected_socktype
    assert any(
        isinstance(filter, AttributeAdder) and filter._attr_key == "job_name"
        for filter in syslog_handler.filters
    )
    assert any(
        isinstance(filter, AttributeAdder) and filter._attr_key == "attempt_id"
        for filter in syslog_handler.filters
    )


def test_configure_syslog_handler_disabled(mock_job_context):
    syslog_handler = configure_syslog_handler(
        False, "localhost", 514, "UDP", "test_job", "12345"
    )
    assert syslog_handler is None


def test_configure_syslog_handler_invalid_protocol(mock_job_context):
    with pytest.raises(ValueError):
        configure_syslog_handler(
            True, "localhost", 514, "invalid_protocol", "test_job", "12345"
        )
