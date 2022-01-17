# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from pydantic import error_wrappers
from pydantic import ValidationError


class TemplateParametersError(Exception):
    __slots__ = "cause", "template_name"

    def __init__(self, cause: ValidationError, template_name: str) -> None:
        self.cause = cause
        self.template_name = template_name

    def __str__(self) -> str:
        validation_errors = self.cause.errors()
        no_errors = len(validation_errors)
        return (
            f'{no_errors} validation error{"" if no_errors == 1 else "s"} for {self.template_name} template\n'
            f"{error_wrappers.display_errors(validation_errors)}"
        )
