begin
    execute immediate 'DROP TABLE "test_table"';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
