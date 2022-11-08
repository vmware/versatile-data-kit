# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from vdk.api.job_input import IJobInput
from vdk.internal.builtin_plugins.run.step import Step

log = logging.getLogger(__name__)

# The function accept NotebookStep (below class) and IJobInput and
# return true if the step has been executed and false if it is not (valid) executable step.
# On error it's expected to raise an exception.
NotebookStepFunction = Callable[["NotebookStep", IJobInput], bool]


@dataclass
class NotebookStep(Step):
    """
    A notebook step that will be executed when running a data job.
    """

    def __init__(self, name, type, runner_func, file_path, job_dir, code):
        super().__init__(name, type, runner_func, file_path, job_dir)
        self.runner_func = runner_func
        self.code = code
