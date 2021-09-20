-- table_source is being populated during execution of vdk-pdt-impala (Post Deployment Test).
INSERT INTO TABLE {db}.{table_destination} PARTITION (pa__arrival_ts)
	SELECT uuid, 'sql', hostname, pa__arrival_ts FROM {db}.{table_source};
