INSERT INTO "{target_schema}"."{target_table}"
(
  SELECT *
  FROM   "{staging_schema}"."{staging_table}"
)
