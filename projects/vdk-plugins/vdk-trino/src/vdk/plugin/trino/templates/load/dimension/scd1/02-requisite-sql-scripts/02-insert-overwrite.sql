-- https://trino.io/docs/current/appendix/from-hive.html#overwriting-data-on-insert
INSERT INTO TABLE {target_schema}.{target_table} {_vdk_template_insert_partition_clause}
SELECT * FROM {source_schema}.{source_view};
