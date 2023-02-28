# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib

from IPython import get_ipython
from IPython.core.magic_arguments import argument
from IPython.core.magic_arguments import magic_arguments
from IPython.core.magic_arguments import parse_argstring
from vdk.internal.builtin_plugins.run import standalone_data_job


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
        self.job = standalone_data_job.StandaloneDataJob(
            name=name,
            template_name=template,
            job_args=job_args,
            data_job_directory=path,
        )
        self.job_input = None

    def get_initialized_job_input(self):
        """
        Get initialised IJobInput object for the current job if present
            :return:  an IJobInput object
        """
        if not self.job_input:
            self.job_input = self.job.__enter__()
        return self.job_input

    # TODO: should automate calling finalize (if it is not called explicitly)
    def finalize(self):
        self.job.__exit__(None, None, None)
        self.job_input = None


def load_ipython_extension(ipython):
    """
    Function that registers %reload_VDK magic
    IPython will look for this function specifically.
    See https://ipython.readthedocs.io/en/stable/config/extensions/index.html
    """
    ipython.register_magic_function(magic_load_job, magic_name="reload_VDK")


# TODO: add extra-plugins option
@magic_arguments()
@argument("-p", "--path", type=str, default=None)
@argument("-n", "--name", type=str, default=None)
@argument("-a", "--arguments", type=str, default=None)
@argument("-t", "--template", type=str, default=None)
def magic_load_job(line: str):
    """
        %reload_data_job magic function which parses arguments from the magic
        and calls function for loading JobControl object
    You can use %initialize_data_job line magic within your Notebook to reload the data_job which is an instance of
    JobControl. Using it you can get an initialized job_input variable and work with it.
    See more for line magic: https://ipython.readthedocs.io/en/stable/interactive/magics.html
    """
    args = parse_argstring(magic_load_job, line)
    load_job(args.path, args.name, args.arguments, args.template)


def load_job(
    path: str = None, name: str = None, arguments: str = None, template: str = None
):
    job = JobControl(path, name, arguments, template)
    get_ipython().push(variables={"VDK": job})
