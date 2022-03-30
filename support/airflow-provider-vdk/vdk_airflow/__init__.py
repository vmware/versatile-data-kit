# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0


def get_provider_info():
    return {
        "package-name": "airflow-provider-vdk'",
        "name": "Versatile Data Kit Airflow Provider",
        "description": "Airflow provider for Versatile Data Kit.",
        "hook-class-names": ["vdk_airflow.hooks.vdk.VDKHook"],
        "extra-links": ["vdk_airflow.operators.vdk.TODO"],
        "versions": ["0.0.1"],
    }
