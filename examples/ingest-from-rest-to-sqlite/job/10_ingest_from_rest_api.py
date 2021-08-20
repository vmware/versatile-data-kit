# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0


def run(job_input):
    job_input.execute_query("DROP TABLE IF EXISTS employees_with_customers")
    job_input.execute_query(
        "CREATE TABLE employees_with_customers AS SELECT * FROM employees WHERE 0;"
    )
    job_input.execute_query(
        """
        INSERT INTO employees_with_customers
        SELECT * FROM employees WHERE EmployeeId IN (SELECT SupportRepId FROM customers);
        """
    )
