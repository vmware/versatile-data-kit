begin
    execute immediate 'drop table oracle_mixed_case_no_inference';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
