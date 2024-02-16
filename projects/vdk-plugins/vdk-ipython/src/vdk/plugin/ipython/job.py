# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import atexit
import json
import logging
import os
import pathlib

from IPython import get_ipython
from IPython.core.magic_arguments import argument
from IPython.core.magic_arguments import magic_arguments
from IPython.core.magic_arguments import parse_argstring
from vdk.api.job_input import IJobInput
from vdk.internal.builtin_plugins.run import standalone_data_job

log = logging.getLogger(__name__)


class JobControl:
    """
    A class introducing an easier way to  work with IStandaloneDataJob instances
    Arguments:
            path: str
                The source code of the data job that will be executed.
            name: str
                The name of the job.  If omitted will be inferred from the director name.
            arguments: str
                Allows for users to pass arguments to data job run.
                Data Job arguments are also used for parameter substitution in queries, see execute_query docstring.
            template: str
                Template name, in case the data job is a template execution.
    """

    def __init__(
        self,
        path: str = None,
        name: str = None,
        arguments: str = None,
        template: str = None,
    ):
        path = pathlib.Path(path) if path else pathlib.Path(os.getcwd())
        job_args = json.loads(arguments) if arguments else None
        self._name = path.name if not name else name
        self._path = path
        self._arguments = job_args
        self._template = template
        self.job = None
        self.job_input = None
        log.debug(
            f"Job Control for job with name {self._name} from path {self._path} "
            f"with arguments {self._arguments} and template {self._template}"
        )

    def get_initialized_job_input(self) -> IJobInput:
        """
        Get initialised IJobInput object for the current job if present
            :return:  an IJobInput object
        """
        if not self.job_input:
            self.job = standalone_data_job.StandaloneDataJob(
                name=self._name,
                template_name=self._template,
                job_args=self._arguments,
                data_job_directory=self._path,
            )
            self.job_input = self.job.__enter__()
        return self.job_input

    def finalize(self):
        """
        Finalise the current job
        """
        if self.job:
            self.job.__exit__(None, None, None)
            self.job_input = None
        else:
            log.warning(
                "You are trying to finalize a job that does not exist.\n"
                "Initialize a job using VDK.get_initialized_job_input() first. "
            )


def load_job(
    path: str = None,
    name: str = None,
    arguments: str = None,
    template: str = None,
    log_level_vdk: str = "WARNING",
):
    if log_level_vdk:
        logging.getLogger("vdk").setLevel(log_level_vdk)
    job = JobControl(path, name, arguments, template)
    get_ipython().push(variables={"VDK": job})

    def finalize_atexit():
        job.finalize()

    atexit.register(finalize_atexit)


@magic_arguments()
@argument("-p", "--path", type=str, default=None)
@argument("-n", "--name", type=str, default=None)
@argument("-a", "--arguments", type=str, default=None)
@argument("-t", "--template", type=str, default=None)
@argument("-l", "--log-level-vdk", type=str, default="WARNING")
def magic_load_job(line: str):
    """
        %reload_data_job magic function which parses arguments from the magic
        and calls function for loading JobControl object
    You can use %reload_VDK line magic within your Notebook to reload the VDK which is an instance of
    JobControl. Using its get_initialized_job_input() method can get an initialized job_input variable to work with.
    See more for line magic: https://ipython.readthedocs.io/en/stable/interactive/magics.html
    """
    # TODO: add extra-plugins option
    args = parse_argstring(magic_load_job, line)
    load_job(args.path, args.name, args.arguments, args.template, args.log_level_vdk)
