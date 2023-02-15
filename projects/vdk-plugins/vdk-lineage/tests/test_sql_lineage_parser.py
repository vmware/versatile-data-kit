# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.lineage.model.sql.model import LineageTable
from vdk.plugin.lineage.sql_lineage_parser import get_table_lineage_from_query


def test_get_insert_table_lineage_from_query_complex():
    query = """
      -- job_name: stage-processing-hourly
      -- op_id: stage-processing-hourly-1647557100-ccrrw
      -- template: vdk.templates.load.dimension.scd2
      /* TO DO DROP AND RECREATE TARGET TABLE ON FULL RELOAD OR DATA TYPE CHANGE */
      -- DROP TABLE stg.dim_sddc_h;
      -- CREATE TABLE stg.dim_sddc_h STORED AS PARQUET AS SELECT * FROM stg.stg_dim_sddc_h;
      -- /* +SHUFFLE */ below is a query hint to Impala. -- Do not remove! https://www.cloudera.com/documentation/enterprise/5-9-x/topics/impala_hints.html
    INSERT OVERWRITE TABLE stg.dim_sddc_h /* +SHUFFLE */
        WITH
        -- filter from the target all elements that define non-current state and are not updated/present in the source
     tgt_filtered AS (
        SELECT
            *
        FROM
            stg.dim_sddc
        WHERE
            valid_to_ts != '2999-01-01 00:00:00'
            AND CONCAT(CAST(dim_sddc_id AS STRING),
            CAST(valid_from_ts AS STRING)) NOT IN (
            SELECT
                CONCAT(CAST(dim_sddc_id AS STRING),
                CAST(valid_from_ts AS STRING))
            FROM
                processing_stg.vw_dim_sddc_h ) ),
        -- filter from the source all elements which are present in
     tgt_filtered src_filtered AS (
        SELECT
            *
        FROM
            processing_stg.vw_dim_sddc_h
        WHERE
            CONCAT(CAST(dim_sddc_id AS STRING),
            CAST(valid_from_ts AS STRING)) NOT IN (
            SELECT
                CONCAT(CAST(dim_sddc_id AS STRING),
                CAST(valid_from_ts AS STRING))
            FROM
                tgt_filtered ) ) (
        SELECT
            *
        FROM
            tgt_filtered )
    UNION ALL (
    SELECT
        COALESCE(tgt.dim_sddc_h_id,
        uuid()),
        src.*
    FROM
        src_filtered AS src
    LEFT JOIN stg.dim_sddc_h AS tgt ON
        src.dim_sddc_id = tgt.dim_sddc_id
        AND src.valid_from_ts = tgt.valid_from_ts )
    """
    lineage_data = get_table_lineage_from_query(query, "test_schema", "test_catalog")

    expected_input_tables = [
        LineageTable("test_catalog", "processing_stg", "vw_dim_sddc_h"),
        LineageTable("test_catalog", "stg", "dim_sddc"),
        LineageTable("test_catalog", "test_schema", "src_filtered"),
        LineageTable("test_catalog", "stg", "dim_sddc_h"),
    ]
    assert set(lineage_data.input_tables) == set(expected_input_tables)

    assert lineage_data.output_table == LineageTable(
        "test_catalog", "stg", "dim_sddc_h"
    )


def test_get_select_table_lineage_from_query_complex():
    query = """
    with ranked_phases as (
      select
          id, name, detail, avg_time_nanos,
          row_number() over (partition by id order by avg_time_nanos desc ) as rank_num
      from staging.stats, default_stats
      where
        pa__collector_instance_id like '%prod%'
        and cast(pa__arrival_day as timestamp) > utc_timestamp() - interval 22 days
        and pa__arrival_ts > utc_timestamp() - interval 21 day
        and num_rows > 0
    )
    select *
    from history.production.query_details
    join ranked_phases
    using (id)
    where detail ilike '%NULL AWARE%'
    order by rank_num , avg_time_nanos desc
    """
    lineage_data = get_table_lineage_from_query(query, "test_schema", "test_catalog")

    expected_input_tables = [
        LineageTable("test_catalog", "staging", "stats"),
        LineageTable("test_catalog", "test_schema", "default_stats"),
        LineageTable("history", "production", "query_details"),
    ]
    assert set(lineage_data.input_tables) == set(expected_input_tables)
