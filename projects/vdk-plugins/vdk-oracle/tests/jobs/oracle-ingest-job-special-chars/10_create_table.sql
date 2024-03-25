create table ingest_special_chars (
    id number,
    "@str_data" varchar2(255),
    "%int_data" number,
    "*float*data*" float,
    bool_data number(1),
    timestamp_data timestamp,
    decimal_data decimal(14,8),
    primary key(id))
