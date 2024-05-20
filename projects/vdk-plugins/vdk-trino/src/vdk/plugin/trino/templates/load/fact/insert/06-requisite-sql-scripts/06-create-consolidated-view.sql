CREATE VIEW {view_schema}.{view_name}
AS
(
    SELECT *
    FROM {staging_schema}.{staging_table}
)
