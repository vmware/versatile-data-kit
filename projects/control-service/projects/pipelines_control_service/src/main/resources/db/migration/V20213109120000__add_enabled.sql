alter table data_job
    add IF NOT EXISTS enabled BOOLEAN DEFAULT TRUE;
