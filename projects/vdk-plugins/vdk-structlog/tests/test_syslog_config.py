import logging
import logging.handlers
import re
import socket
from io import StringIO

from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.structlog.syslog_config import configure_syslog_handler, JobContextFilter, DETAILED_FORMAT


import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_job_context():
    job_context = MagicMock(spec=JobContext)
    core_context_mock = MagicMock()
    configuration_mock = MagicMock()
    configuration_mock.get_value.side_effect = lambda key: {
        "SYSLOG_ENABLED": True,
        "SYSLOG_HOST": "localhost",
        "SYSLOG_PORT": 514,
        "SYSLOG_PROTOCOL": "UDP"
    }.get(key, None)
    core_context_mock.configuration = configuration_mock
    job_context.core_context = core_context_mock
    return job_context


def test_configure_syslog_handler_enabled(mock_job_context):
    syslog_handler = configure_syslog_handler(mock_job_context, "test_job", "12345")
    assert isinstance(syslog_handler, logging.handlers.SysLogHandler)
    assert syslog_handler.level == logging.DEBUG
    assert any(isinstance(filter, JobContextFilter) for filter in syslog_handler.filters)
    assert syslog_handler.formatter._fmt == DETAILED_FORMAT


@pytest.mark.parametrize("protocol", ["UDP", "TCP"])
@patch('socket.socket')
def test_configure_syslog_handler_with_different_protocols(mock_socket, protocol, mock_job_context):
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance

    mock_job_context.core_context.configuration.get_value.side_effect = lambda key: {
        "SYSLOG_ENABLED": True,
        "SYSLOG_HOST": "localhost",
        "SYSLOG_PORT": 514,
        "SYSLOG_PROTOCOL": protocol
    }.get(key, None)

    syslog_handler = configure_syslog_handler(mock_job_context, "test_job", "12345")

    expected_socktype = socket.SOCK_DGRAM if protocol == "UDP" else socket.SOCK_STREAM
    assert mock_socket.called
    assert mock_socket.call_args[0][1] == expected_socktype


def test_configure_syslog_handler_disabled(mock_job_context):
    mock_job_context.core_context.configuration.get_value.side_effect = lambda key: {
        "SYSLOG_ENABLED": False
    }.get(key, None)

    syslog_handler = configure_syslog_handler(mock_job_context, "test_job", "12345")
    assert syslog_handler is None


def test_configure_syslog_handler_invalid_protocol(mock_job_context):
    mock_job_context.core_context.configuration.get_value.side_effect = lambda key: {
        "SYSLOG_ENABLED": True,
        "SYSLOG_HOST": "localhost",
        "SYSLOG_PORT": 514,
        "SYSLOG_PROTOCOL": "invalid_protocol"
    }.get(key, None)

    with pytest.raises(ValueError):
        configure_syslog_handler(mock_job_context, "test_job", "12345")


@patch('logging.handlers.SysLogHandler')
def test_syslog_handler_configuration(mock_syslog_handler, mock_job_context):
    mock_job_context.core_context.configuration.get_value.side_effect = lambda key: {
        "SYSLOG_ENABLED": True,
        "SYSLOG_HOST": "localhost",
        "SYSLOG_PORT": 514,
        "SYSLOG_PROTOCOL": "UDP"
    }.get(key, None)
    configure_syslog_handler(mock_job_context, "test_job", "12345")
    mock_syslog_handler.assert_called_with(address=('localhost', 514),
                                           facility=logging.handlers.SysLogHandler.LOG_USER,
                                           socktype=socket.SOCK_DGRAM)
