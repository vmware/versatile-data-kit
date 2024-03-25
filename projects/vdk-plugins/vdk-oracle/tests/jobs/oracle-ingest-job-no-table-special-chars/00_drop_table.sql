begin
    execute immediate 'drop table no_table_special_chars';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
