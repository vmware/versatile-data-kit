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
    Here the actual unary encoding differential private algorithm is implemented.
    """

    def __init__(self, p: float, q: float):
        self._p = p
        self._q = q

    def privatize(self, value: str, domain: List[str]) -> List[int]:
        return self.perturb(one_hot_encode(value, domain))

    def aggregate(self, responses: List[List[int]]) -> List[int]:
        sums = np.sum(responses, axis=0)
        n = len(responses)

        return [(v - n * self._q) / (self._p - self._q) for v in sums]

    def perturb(self, encoded_response: List[int]) -> List[int]:
        return [self.perturb_bit(b) for b in encoded_response]

    def perturb_bit(self, bit: int) -> int:
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
