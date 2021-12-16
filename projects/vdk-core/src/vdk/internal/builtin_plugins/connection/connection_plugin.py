# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.context import CoreContext
from vdk.internal.core.statestore import CommonStoreKeys


class QueryDecoratorPlugin:
    """
    Prefix each DB query with job name and operation ID
    """

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        self._job_name = context.name

    @hookimpl
    def vdk_initialize(self, context: CoreContext) -> None:
        self._op_id = context.state.get(CommonStoreKeys.OP_ID)

    @hookimpl
    def db_connection_decorate_operation(
        self, decoration_cursor: DecorationCursor
    ) -> None:
        managed_operation = decoration_cursor.get_managed_operation()
        managed_operation.set_operation(
            "\n".join(
                ["-- job_name: {job_name}", "-- op_id: {op_id}", "{operation}"]
            ).format(
                job_name=self._job_name,
                op_id=self._op_id,
                operation=managed_operation.get_operation(),
            )
        )
