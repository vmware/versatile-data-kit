alter table if exists data_job
    add column if not exists last_execution_status smallint;
alter table if exists data_job
    add column if not exists last_execution_end_time timestamp;
alter table if exists data_job
    add column if not exists last_execution_duration int;
