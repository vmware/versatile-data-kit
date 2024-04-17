begin
    execute immediate 'drop table data_frame_schema_inference';
    exception when others then if sqlcode <> -942 then raise; end if;
end;
