alter table if exists data_job_deployment
    rename column resources_cpu_request to resources_cpu_request_cores;

alter table if exists data_job_deployment
    rename column resources_cpu_limit to resources_cpu_limit_cores;

alter table if exists data_job_deployment
    rename column resources_memory_request to resources_memory_request_mi;

alter table if exists data_job_deployment
    rename column resources_memory_limit to resources_memory_limit_mi;
