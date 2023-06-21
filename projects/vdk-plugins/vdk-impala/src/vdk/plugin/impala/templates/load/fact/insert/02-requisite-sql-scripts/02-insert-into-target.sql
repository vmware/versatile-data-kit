-- /* +SHUFFLE */ below is a query hint to Impala.
-- Do not remove! https://www.cloudera.com/documentation/enterprise/5-9-x/topics/impala_hints.html
INSERT INTO TABLE {target_schema}.{target_table} {_vdk_template_insert_partition_clause} /* +SHUFFLE */
(
  SELECT *
  FROM   {source_schema}.{source_view}
);
