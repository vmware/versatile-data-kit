begin
    execute immediate 'drop table oracle_ingest_case_insensitive';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
