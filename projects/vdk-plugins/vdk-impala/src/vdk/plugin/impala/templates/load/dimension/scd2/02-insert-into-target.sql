/* TO DO DROP AND RECREATE TARGET TABLE ON FULL RELOAD OR DATA TYPE CHANGE */

-- DROP TABLE {target_schema}.{target_table};
-- CREATE TABLE {target_schema}.{target_table} STORED AS PARQUET AS SELECT * FROM  {target_schema}.stg_{target_table};

-- /* +SHUFFLE */ below is a query hint to Impala.
-- Do not remove! https://www.cloudera.com/documentation/enterprise/5-9-x/topics/impala_hints.html
INSERT OVERWRITE TABLE {target_schema}.{target_table} {_vdk_template_insert_partition_clause} /* +SHUFFLE */
WITH
  -- filter from the target all elements that define non-current state and are not updated/present in the source
  tgt_filtered AS (
    SELECT *
    FROM   {target_schema}.{target_table}
    WHERE  {end_time_column} != '{end_time_default_value}'
    AND    CONCAT(CAST({id_column} AS STRING), CAST({start_time_column} AS STRING)) NOT IN (
             SELECT CONCAT(CAST({id_column} AS STRING), CAST({start_time_column} AS STRING))
             FROM   {source_schema}.{source_view}
           )
  ),
  -- filter from the source all elements which are present in tgt_filtered
  src_filtered AS (
    SELECT *
    FROM   {source_schema}.{source_view}
    WHERE  CONCAT(CAST({id_column} AS STRING), CAST({start_time_column} AS STRING)) NOT IN (
             SELECT CONCAT(CAST({id_column} AS STRING), CAST({start_time_column} AS STRING))
             FROM   tgt_filtered
           )
  )
(
  SELECT    *
  FROM      tgt_filtered
)
UNION ALL
(
  SELECT    COALESCE(tgt.{surrogate_key_column}, uuid()), src.*
  FROM      src_filtered AS src
  LEFT JOIN {target_schema}.{target_table} AS tgt
              ON  src.{id_column} = tgt.{id_column}
              AND src.{start_time_column} = tgt.{start_time_column}
)
