# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import hashlib
from typing import Any
from typing import List

import numpy as np


def one_hot_encode(response: str, domain: List[str]) -> List[int]:
    return [1 if d == response else 0 for d in domain]


class DifferentialPrivateUnaryEncoding:
    """
        The class responsible for injecting the noise into the data
    For a detailed description of how unary encoding works please see: https://programming-dp.com/ch13.html#unary-encoding
    """

    def __init__(self, p: float, q: float):
        self._p = p
        self._q = q

    def privatize(self, value: str, domain: List[str]) -> List[int]:
        return self._perturb(one_hot_encode(value, domain))

    def aggregate(self, responses: List[List[int]]) -> List[int]:
        sums = np.sum(responses, axis=0)
        n = len(responses)

        return [(v - n * self._q) / (self._p - self._q) for v in sums]

    def _perturb(self, encoded_response: List[int]) -> List[int]:
        return [self._perturb_bit(b) for b in encoded_response]

    def _perturb_bit(self, bit: int) -> int:
        sample = np.random.random()
        if bit == 1:
            if sample <= self._p:
                return 1
            else:
                return 0
        elif bit == 0:
            if sample <= self._q:
                return 1
            else:
                return 0
