# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import sys

VDK_CONFIG_IPYTHON_KEY = "VDK_CONFIG"


def show_ipython_error(message: str):
    print(f"Error:\n{message}", file=sys.stderr)
