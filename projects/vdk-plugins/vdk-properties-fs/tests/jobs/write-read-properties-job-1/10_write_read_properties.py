# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    my_props = {"key": "value"}
    job_input.set_all_properties(my_props)
    assert job_input.get_all_properties() == my_props

    my_props_updated = {"key": "new_value1", "another_key": "value1"}
    job_input.set_all_properties(my_props_updated)
    assert job_input.get_property("key") == "new_value1"
    assert job_input.get_property("another_key") == "value1"
