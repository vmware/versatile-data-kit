# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
The code is adapted from: https://github.com/vuolter/autoupgrade
"""
import http.client
import logging
import re
import urllib.request

import pkg_resources

log = logging.getLogger(__name__)


class Package:
    """
    PackageCheck class, holds one package.
    """

    __slots__ = ["index", "pkg", "http"]

    def __init__(self, pkg, index):
        """
        Args:
            pkg (str): name of package
            index (str): alternative index, if not given build artifactory will be used. Include
                         full index url, e.g. https://example.com/simple
        """
        self.pkg = pkg
        self.index = index.rstrip("/")
        self.http = urllib.request

    def check(self) -> bool:
        """
        Check if pkg has a later version
        Returns true if later version exists
        """
        log.debug(f"Check version for package {self.pkg} from index {self.index} ...")
        current = self._get_current()
        highest = self._get_highest_version_from_index()
        log.debug(
            f"Current version of {self.pkg} is {current} and highest is {highest}"
        )

        return highest > current

    def _get_current(self) -> tuple:
        try:
            current = self._ver_to_tuple(
                pkg_resources.get_distribution(self.pkg).version
            )
        except pkg_resources.DistributionNotFound:
            current = (-1,)
        return current

    def _get_highest_version_from_index(self) -> tuple:
        url = f"{self.index}/{self.pkg}/"

        with self.http.urlopen(url, timeout=10) as response:
            response: http.client.HTTPResponse

            if response.status >= 300:
                log.debug(
                    f"Got error status from {url}: {response.status}, {response.read()}. "
                    f"Cannot get higher version for {self.pkg}. "
                )
                return (-1,)

            pattr = fr">{self.pkg}-(.+?)<"
            versions = map(
                self._ver_to_tuple,
                re.findall(pattr, response.read().decode("utf-8"), flags=re.I),
            )
            if not versions:
                return (-1,)

            # Avoid non-stable versions like dev, rc, etc.
            versions = list(versions)
            stable_versions = [i for i in versions if len(i) < 4]

            return max(stable_versions)

    @staticmethod
    def _ver_to_tuple(value):
        """
        Convert version like string to a tuple of integers.
        """
        return tuple(int(_f) for _f in re.split(r"\D+", value) if _f)
