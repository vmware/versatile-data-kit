/* TO DO DROP AND RECREATE TARGET TABLE ON FULL RELOAD OR DATA TYPE CHANGE */

-- DROP TABLE {target_schema}.{target_table};
-- CREATE TABLE {target_schema}.{target_table}  STORED AS PARQUET AS SELECT * FROM  {target_schema}.{target_table};

-- /* +SHUFFLE */ below is a query hint to Impala. Do not remove!
-- See https://www.cloudera.com/documentation/enterprise/5-9-x/topics/impala_hints.html for details.
INSERT OVERWRITE TABLE {target_schema}.{target_table} {_vdk_template_insert_partition_clause} /* +SHUFFLE */
SELECT * FROM {source_schema}.{source_view};
