begin
    execute immediate 'drop table oracle_ingest_blob';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
