# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import unittest

from vdk.plugin.impala.impala_error_classifier import is_impala_user_error


class UserErrorClassification(unittest.TestCase):
    def test_user_error_classification(self):
        from impala.error import HiveServer2Error, OperationalError

        self.assertTrue(
            is_impala_user_error(
                HiveServer2Error(
                    "AuthorizationException: User 'pa__view_incremental_refresh@PHONEHOME.VMWARE.COM' "
                    "does not have privileges to execute 'SELECT' on: default.vm"
                )
            )
        )
        self.assertTrue(
            is_impala_user_error(
                HiveServer2Error(
                    "AnalysisException: Syntax error in line 1:\n"
                    "INSERT ums_reports.vm_usage_details...\n"
                    "       ^\n"
                    "Encountered: IDENTIFIER\n"
                    "Expected: INTO, OVERWRITE, STRAIGHT_JOIN\n"
                    "\n"
                    "CAUSED BY: Exception: Syntax error"
                )
            )
        )
        self.assertTrue(
            is_impala_user_error(
                HiveServer2Error(
                    "AnalysisException: Could not resolve column/field reference: 'nsx'"
                )
            )
        )
        self.assertTrue(
            is_impala_user_error(HiveServer2Error("ArrayIndexOutOfBoundsException: 9"))
        )
        self.assertTrue(
            is_impala_user_error(
                OperationalError("Cancelled from Impala's debug web interface")
            )
        )
        self.assertTrue(
            is_impala_user_error(
                OperationalError(
                    "Query 9a467f0c5086b6fd:6ef6fc200000000 expired due to execution time limit of 1h"
                )
            )
        )
        self.assertTrue(
            is_impala_user_error(
                OperationalError(
                    """Failed to close HDFS file: hdfs://HDFS/user/hive/warehouse/views/databases/tam_vac_data.db/esx_denorm/_impala_insert_staging/eb47dd32fd2ad08d_71fcffee00000000/.eb47dd32fd2ad08d-71fcffee00000064_915917285_dir/engagementid=ENG-23483/pa__arrival_day=1523836800/eb47dd32fd2ad08d-71fcffee00000064_1332602745_data.0.parq
       Error(255): Unknown error 255
       Root cause: RemoteException: The DiskSpace quota of /user/hive/warehouse/views/databases/tam_vac_data.db is exceeded: quota = 32212254720 B = 30 GB but diskspace consumed = 32700353031 B = 30.45 GB"""
                )
            )
        )
        self.assertTrue(
            is_impala_user_error(
                OperationalError(
                    "Cannot perform hash join at node with id 9.Repartitioning "
                    "did not reduce the size of a spilled partition."
                )
            )
        )
        self.assertTrue(
            is_impala_user_error(
                OperationalError(
                    "Scratch space limit of 107374182400 bytes exceeded for query "
                    "while spilling data to disk on backend xxx.com:22000."
                )
            )
        )
        self.assertTrue(
            is_impala_user_error(
                ValueError(
                    "Property last_processed_timestamp is of unsupported type or has unsupported name."
                )
            )
        )
        self.assertTrue(
            is_impala_user_error(
                ValueError(
                    "Value 2021-08-30 08:23:50.273573 for "
                    "property last_processed_timestamp is of unsupported type <class 'datetime.datetime'>."
                )
            )
        )
        self.assertTrue(
            is_impala_user_error(
                HiveServer2Error(
                    "impala.error.HiveServer2Error: UDF ERROR: Decimal expression overflowed"
                )
            )
        )
