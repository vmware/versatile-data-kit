# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import sys


def show_ipython_error(message: str):
    print(f"Error:\n{message}", file=sys.stderr)
