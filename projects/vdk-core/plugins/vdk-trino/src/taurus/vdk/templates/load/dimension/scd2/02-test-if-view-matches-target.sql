(
  SELECT
    NULL as "{sk_column}",
    NULL as "{active_from_column}",
    NULL as "{active_to_column}",
    "{id_column}",
    {value_columns_str}
  FROM
    "{source_schema}"."{source_view}"
  LIMIT 0
)
UNION ALL
(
  SELECT
    *
  FROM
    "{target_schema}"."{target_table}"
  LIMIT 0
)
