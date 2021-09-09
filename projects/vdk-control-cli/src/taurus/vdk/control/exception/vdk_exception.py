# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click as click


class VDKException(click.UsageError):
    """
    The VDKException is custom exception type following the coding standard for error handling:
    see the project contributing documentation
    """

    def __init__(self, what, why, consequence, countermeasure):
        banner = "¯\\_(ツ)_/¯"
        self.message = (
            f"{banner}\n"
            f"\nwhat: {what}\n"
            f"why: {why}\n"
            f"consequences: {consequence}\n"
            f"countermeasures: {countermeasure}\n"
        )
        super().__init__(self.message)
