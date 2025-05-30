# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

# https://packaging.python.org/guides/single-sourcing-package-version/#
try:
    # Change here if project is renamed and does not equal the setuptools metadata.name
    dist_name = "vdk-control-cli"
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:  # pragma: no cover
    __version__ = "unknown"


def build_details():
    try:
        from vdk.internal.control import vdk_control_build_info

        build = [
            f"{key}={value}"
            for key, value in vdk_control_build_info.__dict__.items()
            if not key.startswith("_")
        ]
        return ", ".join(build)
    except:
        return ""
