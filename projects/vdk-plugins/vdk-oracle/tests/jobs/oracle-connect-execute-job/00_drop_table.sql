begin
    execute immediate 'drop table todoitem';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
