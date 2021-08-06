-- TODO: latest_job_termination_status, latest_job_deployment_status, and latest_job_execution_id are currently part of the data_jobs metadata.
-- TODO: In the future, when data jobs can have multiple deployments (and executions per deployment), these should be moved to a separate table(s).
alter table data_job
    add latest_job_execution_id varchar;
