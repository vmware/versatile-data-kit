(SELECT * FROM "{source_schema}"."{source_view}" LIMIT 0)
UNION ALL
(SELECT * FROM "{target_schema}"."{target_table}" LIMIT 0)
