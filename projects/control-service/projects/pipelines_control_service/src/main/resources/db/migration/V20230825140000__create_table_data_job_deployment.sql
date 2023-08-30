create table data_job_deployment
(
    data_job_name            varchar not null primary key references data_job (name) on delete cascade,
    deployment_version_sha   varchar,
    git_commit_sha           varchar,
    python_version           varchar,
    resources_cpu_request    float,
    resources_cpu_limit      float,
    resources_memory_request int,
    resources_memory_limit   int,
    last_deployed_date       timestamp,
    last_deployed_by         varchar,
    enabled                  boolean
)
