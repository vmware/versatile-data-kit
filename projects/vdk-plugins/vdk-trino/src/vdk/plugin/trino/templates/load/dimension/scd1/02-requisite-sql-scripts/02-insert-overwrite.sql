-- https://trino.io/docs/current/appendix/from-hive.html#overwriting-data-on-insert
INSERT INTO {target_schema}.{target_table}
SELECT *
FROM {source_schema}.{source_view}
