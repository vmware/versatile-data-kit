# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from vdk.internal.control.configuration.vdk_config import VDKConfigFolder


@click.command(
    short_help="Logout the user from the Data Jobs Service.",
    help="Logout the user from the Data Jobs Service by deleting their refresh token stored locally.",
)
def logout():
    conf = VDKConfigFolder()
    conf.delete_credentials()
