begin
    execute immediate 'drop table ingest_special_chars';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
