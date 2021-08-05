-- TODO: latest_job_termination_status and latest_job_deployment_status are currently part of the data_jobs metadata.
-- TODO: In the future, when data jobs can have multiple deployments, these should be moved to a separate table.
alter table data_job
    add latest_job_termination_status varchar;
