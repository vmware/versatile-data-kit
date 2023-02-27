# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib

from IPython import get_ipython
from IPython.core.magic_arguments import argument
from IPython.core.magic_arguments import magic_arguments
from IPython.core.magic_arguments import parse_argstring
from vdk.internal.builtin_plugins.run import standalone_data_job


class JobControl:
    """
    The main idea of thi class is to make it easier to  work with IStandaloneDataJob instances
    Since the user will be using this class
    """

    def __init__(
        self,
        path: str = None,
        name: str = None,
        arguments: str = None,
        template: str = None,
    ):
        path = pathlib.Path(path) if path else pathlib.Path(os.getcwd())
        self.job = standalone_data_job.StandaloneDataJob(
            name=name,
            job_args=arguments,
            template_name=template,
            data_job_directory=path,
        )

    def get_initialized_job_input(self):
        return self.job.__enter__()

    def finalise(self):
        self.job.__exit__(None, None, None)


def load_ipython_extension(ipython):
    """
    IPython will look for this function specifically.
    See https://ipython.readthedocs.io/en/stable/config/extensions/index.html
    """
    ipython.register_magic_function(magic_load_job, magic_name="reload_data_job")


# TODO: add exta-plugins option
@magic_arguments()
@argument("-p", "--path", type=str, default=None)
@argument("-n", "--name", type=str, default=None)
@argument("-a", "--arguments", type=str, default=None)
@argument("-t", "--template", type=str, default=None)
def magic_load_job(line: str):
    """
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
    get_ipython().push(variables={"data_job": job})
