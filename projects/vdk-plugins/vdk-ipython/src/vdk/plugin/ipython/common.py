# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import sys


def show_ipython_error(message: str):
    print(f"Error:\n{message}", file=sys.stderr)
