-- create table with same schema as target table
CREATE TABLE "{table_schema}"."{table_name}"(
    LIKE "{target_schema}"."{target_table}"
)
