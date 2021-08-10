# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import sys

from vdk_job_builder.vdk_job_builder import JobConfig


# TODO: create binary which will use this module instead
# of this script here. Possible choices
# https://pypi.org/project/click/
# https://hugovk.github.io/top-pypi-packages/
#
# This is only example implementation which shows
# how the package can be used
if len(sys.argv) == 2:
    print("Job name only requires specific folder structure")
    job_name = sys.argv.__getitem__(1)
    print(f"job_name={job_name}")
    j = JobConfig().with_default_config(job_name)
    j.build_image()
    # j.push_images() # Optional
elif len(sys.argv) == 4:
    print("Job name, Dockerfile location and build context")
    job_name = sys.argv.__getitem__(1)
    dockerfile_path = sys.argv.__getitem__(2)
    source_path = sys.argv.__getitem__(3)
    print(
        f"job_name={job_name}\nsource_path={source_path}\ndockerfile_path={dockerfile_path}"
    )
    j = JobConfig().with_paths_override(job_name, dockerfile_path, source_path)
    j.build_image()
    # j.push_images() # Optional
elif len(sys.argv) == 1:
    print("Configuration from environment variables and Dockerfile defaults")
    j = JobConfig()
    j.build_image()
    # j.push_images() # Optional
