create index if not exists idx_data_job_execution_job_name_start_time
    on data_job_execution (job_name ASC, start_time DESC);
