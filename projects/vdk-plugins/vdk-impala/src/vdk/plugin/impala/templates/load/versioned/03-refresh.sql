-- make sure metadata about the new blocks in the {target_table} is propagated to the other impalad deamons
REFRESH {target_schema}.{target_table};
