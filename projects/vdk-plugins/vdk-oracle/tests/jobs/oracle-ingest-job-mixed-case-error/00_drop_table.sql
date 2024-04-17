begin
    execute immediate 'drop table oracle_ingest_mixed_case_error';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
