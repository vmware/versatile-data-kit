# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import hashlib
from typing import Any
from typing import List

import numpy as np


class DifferentialPrivateUnaryEncoding:
    """
    Here the actual anonymizer algorithm is implemented.

    Currently It is SHA256 but it could easily be change to anything that is necessary.

    """

    @staticmethod
    def privatize(value: str, domain: List[str]):
        perturb(DifferentialPrivateUnaryEncoding.encode(value, domain))


def perturb(encoded_response):
    return [DifferentialPrivateUnaryEncoding.perturb_bit(b) for b in encoded_response]


def encode(response, domain: List[str]):
    return [1 if d == response else 0 for d in domain]


def perturb_bit(bit):
    p = 0.75
    q = 0.25

    sample = np.random.random()
    if bit == 1:
        if sample <= p:
            return 1
        else:
            return 0
    elif bit == 0:
        if sample <= q:
            return 1
        else:
            return 0
