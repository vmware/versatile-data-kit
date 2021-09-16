
# Overview

This data job is used by post_deployment test of VDK.
It does:
- connect to the DB
- reads the latest record from table_source
- inserts it into table_destination

The heartbeat test is supposed to:
- add record in table_source
- wait until the Data Job copies the record
- verify the record is in table_destination
- truncate both tables, so they are ready for next test run

Note: both tables are partitioned by a single 'pa__arrival_ts'
It is done so that the partition can be easily dropped by the test.
