INSERT INTO {db}.{table_destination}
SELECT
    uuid, 'sql', hostname, pa__arrival_ts
FROM {db}.{table_source}
