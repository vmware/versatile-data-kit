# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.control.utils.cli_utils import GqlQueryBuilder
from vdk.internal.control.utils.cli_utils import QueryField


def test_query_builder_simple():
    jobs_builder = GqlQueryBuilder()
    jobs_builder.start().add_return_new("jobs").add_return_new("content").add("jobName")
    assert jobs_builder.build() == "{ jobs { content { jobName }  }  }"


def test_query_builder():
    jobs_builder = GqlQueryBuilder()
    jobs_content = (
        jobs_builder.start()
        .add_return_new("jobs", arguments=dict(pageNumber=1, pageSize=20))
        .add_return_new("content")
    )
    jobs_content.add("jobName")
    jobs_config = jobs_content.add_return_new("config")
    jobs_config.add("team").add("description")
    jobs_config.add_return_new("schedule").add("scheduleCron")

    assert jobs_builder.build() == (
        "{ jobs(pageNumber: 1, pageSize: 20) { content { jobName config { team "
        "description schedule { scheduleCron }  }  }  }  }"
    )


def test_query_builder_with_alias():
    jobs_builder = GqlQueryBuilder()
    jobs_content = (
        jobs_builder.start()
        .add_return_new("jobs", arguments=dict(pageNumber=1, pageSize=20))
        .add_return_new("content")
    )
    starshot_config = jobs_content.add_return_new(
        "config", alias="starshotConfig", arguments={"team": "starshot"}
    )
    eda_config = jobs_content.add_return_new(
        "config", alias="edaConfig", arguments={"team": "eda"}
    )
    starshot_config.add("team").add("description")
    eda_config.add("team").add("description")

    assert jobs_builder.build() == (
        "{ jobs(pageNumber: 1, pageSize: 20) { content { starshotConfig: config(team: "
        "starshot) { team description }  edaConfig: config(team: eda) { team "
        "description }  }  }  }"
    )
