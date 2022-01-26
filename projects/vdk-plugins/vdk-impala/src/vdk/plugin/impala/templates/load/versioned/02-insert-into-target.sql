/* TO DO DROP AND RECREATE TARGET TABLE ON FULL RELOAD OR DATA TYPE CHANGE */

-- DROP TABLE {target_schema}.{target_table};
-- CREATE TABLE {target_schema}.{target_table} STORED AS PARQUET AS SELECT * FROM  {target_schema}.stg_{target_table};

-- /* +SHUFFLE */ below is a query hint to Impala.
-- Do not remove! https://www.cloudera.com/documentation/enterprise/5-9-x/topics/impala_hints.html
INSERT OVERWRITE TABLE {target_schema}.{target_table} {_vdk_template_insert_partition_clause} /* +SHUFFLE */
WITH
  -- Compute the union of the source and target tables and augment each side with the following columns:
  -- `_values_hash`:
  --     A hash of the tracked values.
  -- `_lineage`:
  --     Tag the record source (either "source" or "target").
  `{target_table}_union` AS (
    (
      SELECT
        'source' AS `_lineage`,
        -- FIXME: change from '#' to NULL results in collision
        FNV_HASH(
          CONCAT_WS('|',
            {hash_expr_str}
          )
        ) AS `_values_hash`,
        UUID() as `{sk_column}`,
        `{updated_at_column}` AS `{active_from_column}`,
        CAST("9999-12-31" AS TIMESTAMP) AS `{active_to_column}`,
        `{id_column}`,
        {value_columns_str}
      FROM
        `{source_schema}`.`{source_view}`
    )
    UNION ALL
    (
      SELECT
        'target' AS `_lineage`,
        -- FIXME: change from '#' to NULL results in collision
        FNV_HASH(
          CONCAT_WS('|',
            {hash_expr_str}
          )
        ) AS `_values_hash`,
        `{sk_column}`,
        `{active_from_column}`,
        `{active_to_column}`,
        `{id_column}`,
        {value_columns_str}
      FROM
        `{target_schema}`.`{target_table}`
    )
  ),
  -- Extend `{target_table}_union` with the following expressions:
  -- `_is_overridden`:
  --     True if and only if the record is overridden by a following record in a partition of records that share the
  --     same primary key and start time, where "target" records are listed before "source".
  -- `{sk_column}`, `{active_to_column}`:
  --     The first value of that column from the partition of records sharing the same primary key and start time,
  --     where "target" records are listed before "source".
  -- The result set is ready for elimination of overridden records.
  `{target_table}_union_extended_v1` AS (
    SELECT
      `_lineage`,
      `_values_hash`,
      LEAD(TRUE, 1, FALSE) OVER(
        PARTITION BY `{id_column}`, `{active_from_column}`
        ORDER BY `_lineage` DESC
      ) AS `_is_overridden`,
      FIRST_VALUE(`{sk_column}`) OVER(
        PARTITION BY `{id_column}`, `{active_from_column}`
        ORDER BY `_lineage` DESC
      ) AS `{sk_column}`,
      `{active_from_column}`,
      FIRST_VALUE(`{active_to_column}`) OVER(
        PARTITION BY `{id_column}`, `{active_from_column}`
        ORDER BY `_lineage` DESC
      ) AS `{active_to_column}`,
      `{id_column}`,
      {value_columns_str}
    FROM
      `{target_table}_union`
  ),
  -- Exclude overridden records from `{target_table}_union_extended_v1` and
  -- extend the result with the following expressions:
  -- `_merge_with_previous`:
  --     A boolean flag indicating whether the record will be merged with the previous record within a partition of
  --     records that share the same primary key and values hash and are ordered by their "active from" timestamp.
  -- The result set is ready for merging of adjacent records with the same values hash.
  `{target_table}_union_extended_v2` AS (
    SELECT
      LAG(`_values_hash`, 1, 0) OVER(
        PARTITION BY `{id_column}`
        ORDER BY `{active_from_column}`
      ) = `_values_hash` AS `_merge_with_previous`,
      `{sk_column}`,
      `{active_from_column}`,
      `{active_to_column}`,
      `{id_column}`,
      {value_columns_str}
    FROM
      `{target_table}_union_extended_v1`
    WHERE
      `_is_overridden` = FALSE
  )
  -- Exclude records that are merged with the preceding record and fix the "active to" timestamp.
  SELECT
    `{sk_column}`,
    `{active_from_column}`,
    LEAD(`{active_from_column}`, 1, '9999-12-31') OVER(
      PARTITION BY `{id_column}`
      ORDER BY `{active_from_column}`
    ) AS `{active_to_column}`,
    `{id_column}`,
    {value_columns_str}
  FROM
    `{target_table}_union_extended_v2`
  WHERE
    `_merge_with_previous` = FALSE;
