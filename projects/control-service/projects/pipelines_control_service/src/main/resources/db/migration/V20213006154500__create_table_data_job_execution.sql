create table if not exists data_job_execution (
    id varchar primary key,
    job_name varchar not null references data_job (name) on delete cascade,
    type smallint not null,
    status smallint not null,
    message varchar,
    op_id varchar not null,
    start_time timestamp,
    end_time timestamp,
    job_version varchar,
    job_schedule varchar,
    vdk_version varchar,
    resources_cpu_request float,
    resources_cpu_limit float,
    resources_memory_request int,
    resources_memory_limit int,
    last_deployed_date timestamp,
    last_deployed_by varchar,
    started_by varchar
);

COMMENT ON COLUMN data_job_execution.resources_memory_request IS 'Memory request in megabytes';
COMMENT ON COLUMN data_job_execution.resources_memory_limit IS 'Memory limit in megabytes';
