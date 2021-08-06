create table data_job (
   name varchar primary key,
   team varchar,
   description varchar,
   schedule varchar,
   notified_on_job_failure_user_error varchar,
   notified_on_job_failure_platform_error varchar,
   notified_on_job_success varchar,
   notified_on_job_deploy varchar,
   name_deprecated varchar
)
