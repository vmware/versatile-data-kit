alter table if exists data_job_execution
    add column if not exists job_python_version varchar;
