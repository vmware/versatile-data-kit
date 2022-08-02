# Versatile Data Kit Airflow provider

A set of Airflow operators, sensors and a connection hook intended to help schedule Versatile Data Kit jobs using Apache Airflow.

# Usage

To install it simply run:
```
pip install airflow-provider-vdk
```

Then you can create a workflow of data jobs (deployed by VDK Control Service) like this:

```
from datetime import datetime

from airflow import DAG
from vdk_provider.operators.vdk import VDKOperator

with DAG(
    "airflow_example_vdk",
    schedule_interval=None,
    start_date=datetime(2022, 1, 1),
    catchup=False,
    tags=["example", "vdk"],
) as dag:
    trino_job1 = VDKOperator(
        conn_id="vdk-default",
        job_name="airflow-trino-job1",
        team_name="taurus",
        task_id="trino-job1",
    )

    trino_job2 = VDKOperator(
        conn_id="vdk-default",
        job_name="airflow-trino-job2",
        team_name="taurus",
        task_id="trino-job2",
    )

    transform_job = VDKOperator(
        conn_id="vdk-default",
        job_name="airflow-transform-job",
        team_name="taurus",
        task_id="transform-job",
    )

    [trino_job1, trino_job2] >> transform_job

```

# Example

See [full example here](https://github.com/vmware/versatile-data-kit/tree/main/examples/airflow-example)

# Demo

You can see demo during one of the community meetings here: https://www.youtube.com/watch?v=c3j1aOALjVU&t=690s

# Architecture

See the [vdk enhancement proposal spec here](https://github.com/vmware/versatile-data-kit/tree/main/specs/vep-554-apache-airflow-integration)
