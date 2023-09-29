create table desired_data_job_deployment
(
    data_job_name               varchar not null primary key references data_job (name) on delete cascade,
    git_commit_sha              varchar,
    python_version              varchar,
    schedule                    varchar,
    resources_cpu_request_cores float,
    resources_cpu_limit_cores   float,
    resources_memory_request_mi int,
    resources_memory_limit_mi   int,
    last_deployed_by            varchar,
    enabled                     boolean
)
