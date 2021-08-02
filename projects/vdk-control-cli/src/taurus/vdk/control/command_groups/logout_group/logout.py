# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from taurus.vdk.control.configuration.vdk_config import VDKConfigFolder


@click.command(
    help="Logout the user from the Data Jobs Service by deleting his refresh token stored locally"
)
def logout():
    conf = VDKConfigFolder()
    conf.delete_credentials()
