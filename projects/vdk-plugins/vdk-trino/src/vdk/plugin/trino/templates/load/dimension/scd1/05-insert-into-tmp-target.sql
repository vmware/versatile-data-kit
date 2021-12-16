INSERT INTO "{target_schema}"."tmp_{target_table}"
(
  SELECT *
  FROM   "{source_schema}"."{source_view}"
)
