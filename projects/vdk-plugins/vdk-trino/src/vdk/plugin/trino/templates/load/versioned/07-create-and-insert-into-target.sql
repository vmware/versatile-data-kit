CREATE TABLE "{target_schema}"."{target_table}" AS
(
SELECT * FROM "{target_schema}"."vdk_tmp_{target_table}"
)
