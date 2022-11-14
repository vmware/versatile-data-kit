# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from github import Github
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):

    # In order to use properties, install vdk server OR vdk-properties-fs plugin
    # [VDK server installation](https://github.com/vmware/versatile-data-kit/wiki/Installation#install-versatile-data-kit-control-service)
    # [vdk-properties-fs plugin](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-properties-fs)

    # Set job properties using following commands:
    # vdk properties --set-secret 'token' -n github-stars-example-job -t yourteam
    # vdk properties --set 'repo_path' -n github-stars-example-job -t yourteam
    properties = job_input.get_all_properties()
    token = job_input.get_property('token')
    repo_path = job_input.get_property('repo_path')

    # Set token and path for PyGithub
    g = Github(token)
    repo = g.get_repo(repo_path)

    # Get Stargazer data with starred date, put them into a list and get length
    users = repo.get_stargazers_with_dates()
    usr_list = list(users)
    count = len(usr_list)

    data_to_send = []

    # Go through the list and add Starred Time and count of stars
    for i, u in enumerate(range(count)):
        data_to_send.append(
            [str(usr_list[u].starred_at), i + 1],
        )
    # Ingest the data in to github_star_history table
    job_input.send_tabular_data_for_ingestion(
        rows=data_to_send,
        column_names=["starred_time", "count"],
        destination_table="github_star_history",
    )
