# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from vdk.internal.core.errors import BaseVdkError
from vdk.internal.core.errors import ResolvableBy


class SecretsException(BaseVdkError):
    """
    Base Exception for all custom exceptions related to the properties.
    """

    def __init__(
        self,
        message: Optional[str] = None,
        resolvable_by: Optional[ResolvableBy] = None,
    ):
        super().__init__(None, resolvable_by, message)


class WritePreProcessSecretsException(SecretsException):
    def __init__(
        self,
        message: Optional[str] = None,
        client="unknown",
        preprocess_sequence: str = "",
        resolvable_by: Optional[ResolvableBy] = None,
    ):
        if not message:
            message = (
                f"Write pre-processor for client {client} failed. "
                f"preprocess sequence  is {preprocess_sequence}. "
                f"No properties are updated."
            )
        super().__init__(message, resolvable_by)
