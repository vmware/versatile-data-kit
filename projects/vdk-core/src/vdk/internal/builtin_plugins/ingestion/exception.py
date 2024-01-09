# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Any
from typing import Optional

from vdk.internal.core.errors import BaseVdkError
from vdk.internal.core.errors import ResolvableBy


class IngestionException(BaseVdkError):
    """
    Base Exception for all custom exceptions related to the ingestion process.
    This is intended to catch general exceptions that do not fit into more specific categories.
    """

    def __init__(self, message: str, resolvable_by: Optional[ResolvableBy] = None):
        super().__init__(None, resolvable_by, message)


class PayloadIngestionException(IngestionException):
    """
    Base Exception for all payload-related issues during the ingestion process.
    """

    def __init__(
        self,
        payload_id: str,
        message: str,
        destination_table: str = "",
        target: str = "",
        resolvable_by: Optional[ResolvableBy] = None,
    ):
        """
        :param payload_id: ID of the payload. This is a way for user to find out which payload failed to ingest.
                           Left empty if such information is not available
        """
        super().__init__(message=message, resolvable_by=resolvable_by)
        # we are purposefully are not putting payload id
        # in the message, so it's not logged in case it's sensitive
        self.payload_id = payload_id
        self.destination_table = destination_table
        self.target = target


class EmptyPayloadIngestionException(PayloadIngestionException):
    """
    Raised when an empty payload is encountered during ingestion and it is not expected.
    """

    def __init__(
        self,
        message: Optional[str] = None,
        resolvable_by: Optional[ResolvableBy] = None,
    ):
        if not message:
            message = "Payload given to ingestion method should not be empty."
        super().__init__(payload_id="", message=message, resolvable_by=resolvable_by)


class InvalidPayloadTypeIngestionException(PayloadIngestionException):
    """
    Raised when the payload provided for ingestion has an invalid type.
    """

    def __init__(
        self,
        payload_id: str,
        expected_type: str,
        actual_type: str,
        message: Optional[str] = None,
        resolvable_by: Optional[ResolvableBy] = None,
    ):
        """
        :param expected_type: The expected type for the payload
        :param actual_type: The actual type of the payload
        """
        if not message:
            message = "Invalid ingestion payload type."
        super().__init__(
            message=f"{message} Expected type: {expected_type}, actual type: {actual_type}.",
            payload_id=payload_id,
            resolvable_by=resolvable_by,
        )


class JsonSerializationIngestionException(PayloadIngestionException):
    """
    Raised when a payload is not JSON-serializable during ingestion.
    """

    def __init__(
        self,
        payload_id: str,
        original_exception: Exception,
        message: str = "",
        resolvable_by: Optional[ResolvableBy] = None,
    ):
        """
        :param original_exception: The original exception triggering this error
        """
        if not message:
            message = "Payload is not json serializable."
        super().__init__(
            message=f"{message} Failure caused by {original_exception}",
            payload_id=payload_id,
            resolvable_by=resolvable_by,
        )


class InvalidArgumentsIngestionException(IngestionException):
    """
    Raised when an argument provided to a data ingestion method does not meet the expected constraints.
    """

    def __init__(
        self,
        param_name: str,
        param_constraint: str,
        actual_value: Any,
        message: str = "",
        resolvable_by: ResolvableBy = None,
    ):
        """
        :param param_name: The name of the parameter that caused the exception.
        :param param_constraint: Description of the constraint that the parameter failed to meet.
        :param actual_value: The actual value that was passed for the parameter.
        """
        super().__init__(
            message=f"Ingestion parameter '{param_name}' is not valid. "
            f"It must match constraint {param_constraint} but was '{actual_value}'. "
            f"{message}",
            resolvable_by=resolvable_by,
        )
        self.param_name = param_name
        self.param_constraint = param_constraint


class PreProcessPayloadIngestionException(PayloadIngestionException):
    """
    Raised when an error occurs during the pre-processing phase of payload ingestion.
    This is specifically when plugin hook pre_ingest_process raises an exception.
    """

    def __init__(
        self,
        payload_id: str,
        destination_table: str,
        target: str,
        message: str,
        resolvable_by: ResolvableBy = None,
    ):
        super().__init__(
            message=message,
            destination_table=destination_table,
            target=target,
            payload_id=payload_id,
            resolvable_by=resolvable_by,
        )


class PostProcessPayloadIngestionException(PayloadIngestionException):
    """
    Raised when an error occurs during the post-processing phase of payload ingestion.
    This is specifically when plugin hook post_ingest_process raises an exception.
    """

    def __init__(
        self,
        payload_id: str,
        destination_table: str,
        target: str,
        message: str,
        resolvable_by: ResolvableBy = None,
    ):
        super().__init__(
            message=message,
            destination_table=destination_table,
            target=target,
            payload_id=payload_id,
            resolvable_by=resolvable_by,
        )
