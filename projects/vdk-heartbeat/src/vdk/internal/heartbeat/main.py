# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import click
from vdk.internal.heartbeat import log_config
from vdk.internal.heartbeat import reporter
from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.hearbeat import Heartbeat

log = logging.getLogger(__name__)


@click.command(
    help="""Heartbeat tool for verifying deployed Versatile Data Kit SDK
and Control Service are functional and working correctly.
It checks that a job can be created, deployed, run and deleted."""
)
@click.option(
    "-f",
    "--config-file",
    default=None,
    type=click.Path(exists=True),
    help="Ini file that contains default configuration for the test. "
    "They need to be set in DEFAULT section."
    "See config.py for what options may be configured. "
    "If there environment variables defined for the same option, they would take precedence.",
)
# @click_log.simple_verbosity_option(logging.getLogger()) # hard to set custom formatter
def run(config_file):
    # TODO: run with pytest perhaps would be better.
    # https://pytest.org/en/6.2.x/usage.html#calling-pytest-from-python-code
    log_config.configure_loggers()
    log.info("Starting vdk heartbeat.")

    config = Config(config_file)
    log_config.configure_loggers(op_id=config.op_id)
    heartbeat = Heartbeat(config)
    try:
        heartbeat.run()
    finally:
        reporter.report_results(config)


if __name__ == "__main__":
    run()
