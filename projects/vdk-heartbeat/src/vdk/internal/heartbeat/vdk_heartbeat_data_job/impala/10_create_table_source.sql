CREATE TABLE IF NOT EXISTS {db}.{table_source}(
    uuid STRING,
    hostname STRING
)
PARTITIONED BY (pa__arrival_ts BIGINT);
