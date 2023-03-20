# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import hashlib
from typing import Any

import numpy as np


class DifferentialPrivateRandomResponse:
    """
    Here the actual anonymizer algorithm is implemented.

    Currently It is SHA256 but it could easily be change to anything that is necessary.

    """

    @staticmethod
    def privatize(value: bool):
        # first coin flip
        if np.random.randint(0, 2) == 0:
            # answer truthfully
            return value
        else:
            # answer randomly (second coin flip)
            return np.random.randint(0, 2) == 0
