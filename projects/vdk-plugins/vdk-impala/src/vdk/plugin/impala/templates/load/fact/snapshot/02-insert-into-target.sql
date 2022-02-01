-- /* +SHUFFLE */ below is a query hint to Impala.
-- Do not remove! https://www.cloudera.com/documentation/enterprise/5-9-x/topics/impala_hints.html
INSERT OVERWRITE TABLE {target_schema}.{target_table} {_vdk_template_insert_partition_clause} /* +SHUFFLE */
(
  SELECT *
  FROM   {target_schema}.{target_table}
  WHERE  {last_arrival_ts} < (SELECT MIN({last_arrival_ts}) FROM {source_schema}.{source_view})
)
UNION ALL
(
  SELECT *
  FROM   {source_schema}.{source_view}
);
