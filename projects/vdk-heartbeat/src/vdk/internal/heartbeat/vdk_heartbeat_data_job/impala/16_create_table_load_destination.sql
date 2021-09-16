CREATE TABLE IF NOT EXISTS {db}.{table_load_destination}(
    uuid STRING,
    hostname STRING,
    pa__arrival_ts BIGINT
) STORED AS PARQUET;
