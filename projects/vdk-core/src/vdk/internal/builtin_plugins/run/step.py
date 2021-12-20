# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import logging
import pathlib
from abc import ABC
from dataclasses import dataclass
from typing import Callable

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


# The function accept Step (below class) and IJobInput and
# return true if the step has been executed and false if it is not (valid) executable step.
# On error it's expected to raise an exception.
StepFunction = Callable[["Step", IJobInput], bool]


@dataclass
class Step(ABC):
    """
    A step that will be executed when running a data job.
    """

    # the name of the concrete step (e.g name of the file)
    name: str
    # string representing a step type (sql or python).
    type: str
    # function that will execute the actual step
    runner_func: StepFunction
    # file where the step is defined
    file_path: pathlib.Path
    # the root job directory
    job_dir: pathlib.Path
    # parent Step
    parent: Step | None = None


@dataclass
class StepBuilder:
    def __init__(self):
        self.__steps: list[Step] = []

    def add_step(self, step: Step) -> None:
        self.__steps.append(step)

    def get_steps(self) -> list[Step]:
        return self.__steps
