INSERT INTO "{target_schema}"."tmp_{target_table}"
(
  SELECT *
  FROM   "{target_schema}"."{target_table}"
)
UNION ALL
(
  SELECT *
  FROM   "{source_schema}"."{source_view}"
)
