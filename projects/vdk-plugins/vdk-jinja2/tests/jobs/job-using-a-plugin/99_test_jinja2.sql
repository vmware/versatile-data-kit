create table table_query_func_test as
select
    {{ query("select * from stocks")[0][0] }} as query_result
