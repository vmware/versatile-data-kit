begin
    execute immediate 'drop table ingest_type_inference';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
