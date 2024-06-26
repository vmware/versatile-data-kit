CREATE VIEW {view_schema}.{view_name}
AS
(
    SELECT *
    FROM {target_schema}.{target_table}
    UNION ALL
    SELECT *
    FROM {staging_schema}.{staging_table}
)
