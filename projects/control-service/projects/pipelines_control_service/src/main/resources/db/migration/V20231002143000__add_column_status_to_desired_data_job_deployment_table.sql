alter table if exists desired_data_job_deployment
    add column if not exists status varchar;
