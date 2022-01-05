create index if not exists idx_data_job_execution_job_name_end_time
    on data_job_execution (job_name ASC, end_time DESC);
