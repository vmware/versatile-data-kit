alter table data_job
    add last_execution_status smallint,
    add last_execution_end_time timestamp,
    add last_execution_duration int;
