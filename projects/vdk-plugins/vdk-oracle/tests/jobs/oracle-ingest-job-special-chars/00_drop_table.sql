begin
    execute immediate 'drop table TEST_TABLE';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
