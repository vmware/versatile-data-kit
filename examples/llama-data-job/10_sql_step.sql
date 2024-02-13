-- SQL scripts are standard SQL scripts. They are executed against Platform OLAP database.
-- Refer to platform documentation for more information.

-- Common uses of SQL steps are:
--    aggregating data from other tables to a new one
--    creating a table or a view that is needed for the python steps

-- Queries in .sql files can be parametrised.
-- A valid query parameter looks like → {parameter}.
-- Parameters will be automatically replaced if there is a corresponding value existing in the IJobInput properties.

CREATE TABLE IF NOT EXISTS hello_world (id NVARCHAR);
