# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
def setup_testing_check(check):
    if check == "use_positive_check":
        check = _sample_check_true
    elif check == "use_negative_check":
        check = _sample_check_false
    return check


def _sample_check_true(tmp_table_name):
    return True


def _sample_check_false(tmp_table_name):
    return False
