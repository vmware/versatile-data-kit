begin
    execute immediate 'drop table ingest_different_payloads';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
