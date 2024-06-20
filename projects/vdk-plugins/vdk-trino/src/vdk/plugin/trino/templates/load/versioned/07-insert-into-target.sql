INSERT INTO "{target_schema}"."{target_table}"
(
  SELECT *
  FROM  "{target_schema}"."tmp_{target_table}"
)