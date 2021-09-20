CREATE TABLE IF NOT EXISTS {db}.{table_destination}(
    uuid STRING,
    query_source STRING,
    hostname STRING
)
PARTITIONED BY (pa__arrival_ts BIGINT);
