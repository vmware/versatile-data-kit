# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Load example input data for an scd2 template test.

The data is constructed working backwards from the current scd2 template definition as follows.

We have a source relation `S` (usually a view) and a target relation `T`. The elements in these two relations are
uniquely identified by the (`{id_column}`, `{start_time_column}`) composite key. An element is said to be "current in (a
relation) R" if and only if its `{end_time_column}` equals the user-defined `{end_time_default_value}` (which usually is
the largest possible timestamp).


We partition the items in `T` according to the following predicates:

- `C`: elements that are current in `T`,
- `P`: elements that are present in `S`,
- `M`: elements that are modified in `S`.

Obviously, it does not make sense to distinguish between modified or unmodified elements if these elements are not
present in `S`. In other words, `M` does not further partition equivalence classes that contain `¬P`.

```
 C ∧ ¬P ∧  M =  C ∧ ¬P ∧ ¬M =  C ∧ ¬P
¬C ∧ ¬P ∧  M = ¬C ∧ ¬P ∧ ¬M = ¬C ∧ ¬P
```

In total, this means that `T` is partitioned into the following six equivalence classes.

```
 C ∧  P ∧  M
 C ∧  P ∧ ¬M
 C ∧ ¬P
¬C ∧  P ∧  M
¬C ∧  P ∧ ¬M
¬C ∧ ¬P
```

The user contract that the load.dimension.scd2 template defines is as follows:

1. Non-current state that is not present in the source view (¬C ∧ ¬P) is retained in the target view.
2. Non-current state that is present in the source view (¬C ∧ P) is overridden in the target view.
3. Current state that is not present in the source view (C ∧ ¬P) is dropped from the target view. In other words,
   all current state should be present in the source view in order to avoid data loss.

The sample data loaded here defines entries for each non-empty class in the target relation. We load the expected
result of the application in a third relation `R`. The data in `R` and in the updated `T` relations should be the same
up to differences in the surrogate keys of the new items present in `S`.
"""
from vdk.api.job_input import IJobInput

__author__ = "VMware, Inc."
__copyright__ = (
    "Copyright 2019 VMware, Inc.  All rights reserved. -- VMware Confidential"
)


def run(job_input: IJobInput) -> None:
    # Step 1: create a table that represents the current state

    # job_input.execute_query(u'''
    #     DROP TABLE IF EXISTS `{target_schema}`.`{target_table}`
    # ''')
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `{target_schema}`.`{target_table}` (
            `{surrogate_key_column}` STRING,
            `{id_column}` SMALLINT,
            `{start_time_column}` TIMESTAMP,
            `{end_time_column}` TIMESTAMP,
            gender CHAR(1),
            name STRING
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        REFRESH `{target_schema}`.`{target_table}`
    """
    )
    job_input.execute_query(
        """
        INSERT OVERWRITE TABLE `{target_schema}`.`{target_table}` VALUES (
            ("p10", 1, "1400-01-01", "9999-12-31", CAST("m" AS CHAR(1)), "Alfred Hitchcock"  ), --  C ∧  P ∧ ¬M

            ("p20", 2, "1400-01-01", "2019-10-24", CAST("m" AS CHAR(1)), "ANDREI TARKOVSKY"  ), -- ¬C ∧ ¬P
            ("p21", 2, "2019-10-24", "9999-12-31", CAST("m" AS CHAR(1)), "Andrii Tarkowski"  ), --  C ∧  P ∧  M

            ("p30", 3, "1400-01-01", "9999-12-31", CAST("m" AS CHAR(1)), "Ingmar Bergman"    ), --  C ∧ ¬P

            ("p40", 4, "1400-01-01", "2009-01-01", CAST("m" AS CHAR(1)), "Laurence WACHOWSKI"), -- ¬C ∧  P ∧  M
            ("p41", 4, "2009-01-01", "9999-12-31", CAST("m" AS CHAR(1)), "Lana Washowski"    ), --  C ∧  P ∧  M

            ("p50", 5, "1400-01-01", "2016-03-01", CAST("m" AS CHAR(1)), "Andrew Wachowski"  ), -- ¬C ∧  P ∧ ¬M
            ("p51", 5, "2016-03-01", "9999-12-31", CAST("f" AS CHAR(1)), "Andrew Wachowski"  )  --  C ∧  P ∧ ¬M
        )
    """
    )
    job_input.execute_query(
        """
        REFRESH `{target_schema}`.`{target_table}`
    """
    )

    # Step 2: create a table that represents the delta to be applied

    # job_input.execute_query(u'''
    #     DROP TABLE IF EXISTS `{source_schema}`.`{source_view}`
    # ''')
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `{source_schema}`.`{source_view}` (
            `{id_column}` SMALLINT,
            `{start_time_column}` TIMESTAMP,
            `{end_time_column}` TIMESTAMP,
            gender CHAR(1),
            name STRING
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        REFRESH `{source_schema}`.`{source_view}`
    """
    )
    job_input.execute_query(
        """
        INSERT OVERWRITE TABLE `{source_schema}`.`{source_view}` VALUES (
            (1, "1400-01-01", "9999-12-31", CAST("m" AS CHAR(1)), "Alfred Hitchcock"  ), -- p10: unmodified

            (2, "2019-10-24", "9999-12-31", CAST("m" AS CHAR(1)), "Andrei Tarkovsky"  ), -- p21: fix typos in name

            (4, "1400-01-01", "2009-01-01", CAST("m" AS CHAR(1)), "Laurence Wachowski"), -- p40: fix case in name
            (4, "2009-01-01", "2018-12-31", CAST("f" AS CHAR(1)), "Lana Washowski"    ), -- p41: fix gender (closing)
            (4, "2018-12-31", "9999-12-31", CAST("f" AS CHAR(1)), "Lana Wachowski"    ), -- p42: change name (new)

            (5, "1400-01-01", "2016-03-01", CAST("m" AS CHAR(1)), "Andrew Wachowski"  ), -- p50: unmodified
            (5, "2016-03-01", "2018-12-31", CAST("f" AS CHAR(1)), "Andrew Wachowski"  ), -- p51: unmodified (closing)
            (5, "2018-12-31", "9999-12-31", CAST("f" AS CHAR(1)), "Lilly Wachowski"   )  -- p52: change name (new)
        )
    """
    )
    job_input.execute_query(
        """
        REFRESH `{source_schema}`.`{source_view}`
    """
    )

    # Step 3: Create a table containing the state expected after updating the current state with the given delta

    # job_input.execute_query(u'''
    #     DROP TABLE IF EXISTS `{expect_schema}`.`{expect_table}`
    # ''')
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `{expect_schema}`.`{expect_table}` (
            `{surrogate_key_column}` STRING,
            `{id_column}` SMALLINT,
            `{start_time_column}` TIMESTAMP,
            `{end_time_column}` TIMESTAMP,
            gender CHAR(1),
            name STRING
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        REFRESH `{expect_schema}`.`{expect_table}`
    """
    )
    job_input.execute_query(
        """
        INSERT OVERWRITE TABLE `{expect_schema}`.`{expect_table}` VALUES (
            ("p10", 1, "1400-01-01", "9999-12-31", CAST("m" AS CHAR(1)), "Alfred Hitchcock"  ), --  C ∧  P ∧ ¬M

            ("p20", 2, "1400-01-01", "2019-10-24", CAST("m" AS CHAR(1)), "ANDREI TARKOVSKY"  ), -- ¬C ∧ ¬P
            ("p21", 2, "2019-10-24", "9999-12-31", CAST("m" AS CHAR(1)), "Andrei Tarkovsky"  ), --  C ∧  P ∧  M

            ("p40", 4, "1400-01-01", "2009-01-01", CAST("m" AS CHAR(1)), "Laurence Wachowski"), -- ¬C ∧  P ∧  M
            ("p41", 4, "2009-01-01", "2018-12-31", CAST("f" AS CHAR(1)), "Lana Washowski"    ), --  C ∧  P ∧  M
            ("p42", 4, "2018-12-31", "9999-12-31", CAST("f" AS CHAR(1)), "Lana Wachowski"    ), --  C ∧  P ∧  M (new)

            ("p50", 5, "1400-01-01", "2016-03-01", CAST("m" AS CHAR(1)), "Andrew Wachowski"  ), -- ¬C ∧  P ∧ ¬M
            ("p51", 5, "2016-03-01", "2018-12-31", CAST("f" AS CHAR(1)), "Andrew Wachowski"  ), --  C ∧  P ∧ ¬M
            ("p52", 5, "2018-12-31", "9999-12-31", CAST("f" AS CHAR(1)), "Lilly Wachowski"   )  --  C ∧  P ∧ ¬M (new)
        )
    """
    )
    job_input.execute_query(
        """
        REFRESH `{expect_schema}`.`{expect_table}`
    """
    )
