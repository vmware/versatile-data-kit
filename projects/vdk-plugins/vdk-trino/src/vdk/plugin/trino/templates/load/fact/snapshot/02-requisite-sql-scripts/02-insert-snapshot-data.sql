INSERT INTO "{staging_schema}"."{staging_table}"
(
  SELECT *
  FROM   "{target_schema}"."{target_table}"
  WHERE  "{last_arrival_ts}" < (SELECT MIN("{last_arrival_ts}") FROM "{source_schema}"."{source_view}")
)
UNION ALL
(
  SELECT *
  FROM   "{source_schema}"."{source_view}"
)
