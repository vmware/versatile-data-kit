alter table if exists actual_data_job_deployment
    drop constraint if exists fk_data_job_name_ref_data_job;
