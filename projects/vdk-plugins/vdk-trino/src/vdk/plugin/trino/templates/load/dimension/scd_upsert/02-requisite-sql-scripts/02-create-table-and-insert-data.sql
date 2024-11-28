CREATE TABLE "{target_schema_staging}"."{target_table_staging}" AS
(
SELECT t.*
FROM "{target_schema}"."{target_table}" AS t
LEFT JOIN "{source_schema}"."{source_view}" AS s ON s."{id_column}" = t."{id_column}"
WHERE s."{id_column}" IS NULL
)
UNION ALL
(
SELECT *
FROM "{source_schema}"."{source_view}"
)
