# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
from typing import Dict

from taurus.api.job_input import ITemplate
from taurus.api.plugin.plugin_input import ITemplateRegistry
from taurus.vdk.builtin_plugins.run.data_job import DataJobFactory
from taurus.vdk.builtin_plugins.run.execution_results import ExecutionResult
from taurus.vdk.core import errors
from taurus.vdk.core.context import CoreContext

log = logging.getLogger(__name__)


class TemplatesImpl(ITemplateRegistry, ITemplate):
    def __init__(
        self,
        job_name: str,
        core_context: CoreContext,
        datajob_factory: DataJobFactory = None,
    ):
        self._job_name = job_name
        self._core_context = core_context
        self._registered_templates: Dict[str, pathlib.Path] = {}
        self._datajob_factory = (
            DataJobFactory() if datajob_factory is None else datajob_factory
        )

    def add_template(self, name: str, template_directory: pathlib.Path):
        if (
            name in self._registered_templates
            and self._registered_templates[name] != template_directory
        ):
            log.warning(
                f"Template with name {name} has been registered with directory {self._registered_templates[name]}."
                f"We will overwrite it with new directory {template_directory} now."
            )
        self._registered_templates[name] = template_directory

    def execute_template(self, name: str, template_args: Dict) -> ExecutionResult:
        log.debug(f"Execute template {name} {template_args}")
        template_directory = self.get_template_directory(name)
        template_job = self._datajob_factory.new_datajob(
            template_directory, self._core_context, name=self._job_name
        )
        return template_job.run(template_args)

    def get_template_directory(self, name: str) -> pathlib.Path:
        if name in self._registered_templates:
            return self._registered_templates[name]
        else:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                log=logging.getLogger(__file__),
                what_happened=f"No registered template with name: {name}.",
                why_it_happened="Template with that name has not been registered",
                consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
                countermeasures="Make sure you have not misspelled the name of the template "
                "or the plugin(s) providing the template is installed. "
                f"Current list of templated is: {list(self._registered_templates.keys())}",
            )
