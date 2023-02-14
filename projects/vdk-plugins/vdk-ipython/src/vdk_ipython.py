# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib

from IPython import get_ipython
from IPython.core.magic_arguments import argument
from IPython.core.magic_arguments import magic_arguments
from IPython.core.magic_arguments import parse_argstring
from vdk.internal.builtin_plugins.run.standalone_data_job import (
    StandaloneDataJobFactory,
)


def load_ipython_extension(ipython):
    """
    IPython will look for this function specifically.
    See https://ipython.readthedocs.io/en/stable/config/extensions/index.html
    """
    ipython.register_magic_function(magic_load_job, magic_name="reload_job_input")


@magic_arguments()
@argument("-p", "--path", type=str, default=None)
@argument("-n", "--name", type=str, default=None)
@argument("-a", "--arguments", type=str, default=None)
@argument("-t", "--template", type=str, default=None)
def magic_load_job(line: str):
    """
    You can use %initialize_vdk_job line magic within your Notebook to reload the job_input variable
    for your current job
    See more for line magic: https://ipython.readthedocs.io/en/stable/interactive/magics.html
    """
    args = parse_argstring(magic_load_job, line)
    load_job(args.path, args.name, args.arguments, args.template)


def load_job(
    path: str = None, name: str = None, arguments: str = None, template: str = None
):
    path = pathlib.Path(path) if path else pathlib.Path(os.getcwd())
    with StandaloneDataJobFactory.create(
        data_job_directory=path, name=name, job_args=arguments, template_name=template
    ) as job_input:
        get_ipython().push(variables={"job_input": job_input})
