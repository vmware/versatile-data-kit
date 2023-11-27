alter table if exists desired_data_job_deployment
    add column if not exists vdk_version varchar;
