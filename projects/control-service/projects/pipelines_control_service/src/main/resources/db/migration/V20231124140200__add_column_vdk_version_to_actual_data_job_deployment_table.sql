alter table if exists actual_data_job_deployment
    add column if not exists vdk_version varchar;
