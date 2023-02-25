# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0


class VDKAuthException(Exception):
    """
    The VDKAuthException is custom exception type following the coding standard
    for error handling: see the project contributing documentation
    """

    def __init__(self, what, why, consequence, countermeasure):
        banner = "¯\\_(ツ)_/¯"
        self.message = (
            f"{banner}\n"
            f"\nWhat: {what}\n"
            f"Why: {why}\n"
            f"Consequences: {consequence}\n"
            f"Countermeasures: {countermeasure}\n"
        )
        super().__init__(self.message)


class VDKInvalidAuthParamError(VDKAuthException):
    """
    The VDKInvalidAuthParamError is a custom exception type derived from
    the base VDKAuthException type. It is raised when a parameter needed
    for authentication is missing/not provided or otherwise invalid.
    """

    def __init__(self, what, why, consequence, countermeasure):
        super().__init__(
            what=what, why=why, consequence=consequence, countermeasure=countermeasure
        )


class VDKLoginFailedError(VDKAuthException):
    """
    The VDKLoginFailedError is a custom exception type derived from the
    base VDKAuthException type. It is raised when an error occurs while
    going through the actual authentication flow, i.e., when something
    happens while connecting to a third party endpoint.
    """

    def __init__(self, what, why, consequence, countermeasure):
        super().__init__(
            what=what, why=why, consequence=consequence, countermeasure=countermeasure
        )


class VDKAuthOSError(VDKAuthException):
    """
    The VDKAuthOSError is a custom exception type derived from the base
    VDKAuthException type. It is raised when an error in the underlying
    Operating System arises.
    """

    def __init__(self, what, why, consequence, countermeasure):
        super().__init__(
            what=what, why=why, consequence=consequence, countermeasure=countermeasure
        )
