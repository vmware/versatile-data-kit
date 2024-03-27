begin
    execute immediate 'drop table oracle_ingest_case_insensitive_neg_one';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
