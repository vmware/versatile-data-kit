# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import hashlib
from typing import Any


class Anonymizer:
    """
    Here the actual anonymizer algorithm is implemented.

    Currently It is SHA256 but it could easily be change to anything that is necessary.

    """

    @staticmethod
    def anonymize(value: Any):
        return hashlib.sha256(f"{value}".encode()).hexdigest()
