# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import hashlib
from typing import Any

import numpy as np


class DifferentialPrivateRandomResponse:
    """
    The class responsible for injecting the noise into the data
    For a detailed description of how random response works please see: https://programming-dp.com/ch13.html#randomized-response
    """
    def __init__(self, random_response_frequency: int):
        self._random_response_frequency = random_response_frequency

    def privatize(self, value: bool):
        # first coin flip
        if np.random.randint(0, self._random_response_frequency) == 0:
            # answer truthfully
            return value
        else:
            # answer randomly (second coin flip)
            return np.random.randint(0, 2) == 0
