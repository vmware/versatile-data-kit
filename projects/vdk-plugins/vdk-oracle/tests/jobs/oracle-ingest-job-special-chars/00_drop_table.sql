begin
    execute immediate 'drop table test_table';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
