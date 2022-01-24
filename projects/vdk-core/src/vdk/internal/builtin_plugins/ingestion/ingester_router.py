# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.api.plugin.plugin_input import IIngesterRegistry
from vdk.internal.builtin_plugins.ingestion.ingester_base import IngesterBase
from vdk.internal.builtin_plugins.ingestion.ingester_configuration import (
    IngesterConfiguration,
)
from vdk.internal.builtin_plugins.run.execution_state import ExecutionStateStoreKeys
from vdk.internal.core import errors
from vdk.internal.core.config import Configuration
from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import PlatformServiceError
from vdk.internal.core.errors import ResolvableBy
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.errors import VdkConfigurationError
from vdk.internal.core.statestore import CommonStoreKeys
from vdk.internal.core.statestore import StateStore


IngesterPluginFactory = Callable[[], IIngesterPlugin]
Payload = Union[Dict, List[Dict]]

log = logging.getLogger(__name__)


class IngesterRouter(IIngesterRegistry):
    """
    Router class for the core Ingestion API. It takes care of routing the
    payloads to their respective ingestion plugins.
    """

    def __init__(self, cfg: Configuration, core_state: StateStore):
        self._cfg: Configuration = cfg
        self._state: StateStore = core_state
        self._log: logging.Logger = logging.getLogger(__name__)
        self._cached_ingesters: Dict[str, IngesterBase] = dict()
        self._ingester_builders: Dict[str, IngesterPluginFactory] = dict()
        self._pre_processor_sequence: List = self.__get_pre_processor_sequence()
        self._initialized_pre_processors: Optional[
            List
        ] = self.__get_initialized_pre_processors()

    def add_ingester_factory_method(
        self,
        method: str,
        ingester_plugin: IngesterPluginFactory,
    ) -> None:
        """
        Add new ingester.
        """
        self._ingester_builders[method.lower()] = ingester_plugin

    def send_object_for_ingestion(
        self,
        payload: dict,
        destination_table: Optional[str] = None,
        method: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
    ):
        # Pre-process payload
        if self._initialized_pre_processors:
            self._log.info(
                "Starting pre-processing of payload with "
                "pre-processing plugin sequence: "
                f"{self._pre_processor_sequence}"
            )
            for pre_processor in self._initialized_pre_processors:
                payload = self.__preprocess_payload_object(
                    pre_processor=pre_processor,
                    payload=payload,
                    destination_table=destination_table,
                    method=method,
                    target=target,
                    collection_id=collection_id,
                )

        # Use the method and target provided by customer, or load the
        # default ones if set. `method` and `target` provided when the
        # method is called take precedence over the ones set with
        # environment variables.
        method = method or self._cfg.get_value("INGEST_METHOD_DEFAULT")
        method = method.lower() if method is not None else None
        target = target or self._cfg.get_value("INGEST_TARGET_DEFAULT")
        self._log.info(
            "Sending object for ingestion with "
            f"method: {method} and target: {target}"
        )

        if method in self._cached_ingesters.keys():
            ingester = self._cached_ingesters.get(method)
            self.__ingest_object(
                ingester=ingester,
                payload=payload,
                destination_table=destination_table,
                method=method,
                target=target,
                collection_id=collection_id,
            )

        elif method in self._ingester_builders.keys():
            ingester = self.__initialize_ingester(method=method)
            self.__ingest_object(
                ingester=ingester,
                payload=payload,
                destination_table=destination_table,
                method=method,
                target=target,
                collection_id=collection_id,
            )
        else:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                log=self._log,
                what_happened=f"Provided method, {method}, has invalid value.",
                why_it_happened=f"VDK was run with method={method}, however {method} is not part of the available ingestion mechanisms.",
                consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
                countermeasures=f"Provide either valid value for method, or install ingestion plugin that supports this type. "
                f"Currently possible values are {list(self._ingester_builders.keys())}",
            )

    def send_tabular_data_for_ingestion(
        self,
        rows: iter,
        column_names: list,
        destination_table: Optional[str] = None,
        method: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
    ):
        # Pre-process the tabular data if any pre-processors are specified
        if self._initialized_pre_processors:
            self._log.info(
                "Starting pre-processing of tabular data with "
                "pre-processing plugin sequence: "
                f"{self._pre_processor_sequence}"
            )

            first_pre_processor = self._initialized_pre_processors.pop(0)
            payload = self.__preprocess_tabular_data(
                pre_processor=first_pre_processor,
                rows=rows,
                column_names=column_names,
                destination_table=destination_table,
                method=method,
                target=target,
                collection_id=collection_id,
            )
            for pre_processor in self._initialized_pre_processors:
                payload = self.__preprocess_payload_object(
                    pre_processor=pre_processor,
                    payload=payload,
                    destination_table=destination_table,
                    method=method,
                    target=target,
                    collection_id=collection_id,
                )

        # Use the method and target provided by customer, or load the
        # default ones if set. `method` and `target` provided when the
        # method is called take precedence over the ones set with
        # environment variables.
        method = method or self._cfg.get_value("INGEST_METHOD_DEFAULT")
        target = target or self._cfg.get_value("INGEST_TARGET_DEFAULT")
        self._log.info(
            "Sending tabular data for ingestion with "
            f"method: {method} and target: {target}"
        )

        if method in self._cached_ingesters.keys():
            ingester = self._cached_ingesters.get(method)
            self.__ingest_tabular_data(
                ingester=ingester,
                rows=rows,
                column_names=column_names,
                destination_table=destination_table,
                method=method,
                target=target,
                collection_id=collection_id,
            )

        elif method in self._ingester_builders.keys():
            ingester = self.__initialize_ingester(method=method)
            self.__ingest_tabular_data(
                ingester=ingester,
                rows=rows,
                column_names=column_names,
                destination_table=destination_table,
                method=method,
                target=target,
                collection_id=collection_id,
            )
        else:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                log=self._log,
                what_happened=f"Provided method, {method}, has invalid value.",
                why_it_happened=f"VDK was run with method={method}, however {method} is not part of the available ingestion mechanisms.",
                consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
                countermeasures=f"Provide either valid value for method, or install ingestion plugin that supports this type. "
                f"Currently possible values are {list(self._ingester_builders.keys())}",
            )

    def __get_pre_processor_sequence(self) -> List:
        test_envs = os.environ
        """ Load pre-process ingestion sequence if any specified. """
        pre_processor_sequence: Optional[str] = self._cfg.get_value(
            "INGEST_PAYLOAD_PREPROCESS_SEQUENCE"
        )
        return pre_processor_sequence.split(",") if pre_processor_sequence else []

    def __get_initialized_pre_processors(self) -> Optional[List]:
        """Initialize pre-process ingestion plugin sequence if any."""
        if self._pre_processor_sequence:
            self._log.info("Initializing pre-process ingestion plugin sequence.")
            return [self.__initialize_ingester(i) for i in self._pre_processor_sequence]
        else:
            return None

    def __preprocess_payload_object(
        self,
        pre_processor: IngesterBase,
        payload: Payload,
        destination_table: Optional[str],
        method: Optional[str],
        target: Optional[str],
        collection_id: Optional[str],
    ) -> Optional[List[Dict]]:
        """
        Send payload to be processed by a pre-process plugin.
        """
        try:
            if isinstance(payload, dict):
                pre_processor.send_object_for_ingestion(
                    payload, destination_table, method, target, collection_id
                )
                pre_processor.close()
                return pre_processor.get_preprocessed_payload()
            else:
                for elem in payload:
                    pre_processor.send_object_for_ingestion(
                        elem, destination_table, method, target, collection_id
                    )
                    pre_processor.close()
                    return pre_processor.get_preprocessed_payload()
        except Exception as e:
            self._log.error(
                "Failed to send object for pre-processing. "
                "Beware of possible data corruption. "
                f"Exception was: {e}"
            )

    def __preprocess_tabular_data(
        self,
        pre_processor: IngesterBase,
        rows: iter,
        column_names: iter,
        destination_table: Optional[str],
        method: Optional[str],
        target: Optional[str],
        collection_id: Optional[str],
    ) -> Optional[List[Dict]]:
        """Send tabular data to be processed by a pre-process plugin"""
        try:
            pre_processor.send_tabular_data_for_ingestion(
                rows, column_names, destination_table, method, target, collection_id
            )
            pre_processor.close()
            return pre_processor.get_preprocessed_payload()
        except Exception as e:
            self._log.error(
                "Failed to send tabular data for pre-processing. " f"Exception was: {e}"
            )
            errors.log_and_rethrow(
                ResolvableBy.USER_ERROR,
                self._log,
                what_happened="Failed to send tabular data for pre-processing",
                why_it_happened=f"Exception was: {e}",
                consequences="Data is not pre-processed and this may lead to "
                "possible data corruption",
                countermeasures="Please look the error message and try to"
                " fix the error and re-try.",
                exception=e,
                wrap_in_vdk_error=True,
            )

    def __ingest_object(
        self,
        ingester: IngesterBase,
        payload: dict,
        destination_table: Optional[str],
        method: Optional[str],
        target: Optional[str],
        collection_id: Optional[str],
    ):
        try:
            ingester.send_object_for_ingestion(
                payload, destination_table, method, target, collection_id
            )
        except Exception as e:
            self._log.error(
                "Failed to send object for ingestion." f"Exception was: {e}"
            )

    def __ingest_tabular_data(
        self,
        ingester: IngesterBase,
        rows: iter,
        column_names: iter,
        destination_table: Optional[str],
        method: Optional[str],
        target: Optional[str],
        collection_id: Optional[str],
    ):
        try:
            ingester.send_tabular_data_for_ingestion(
                rows, column_names, destination_table, method, target, collection_id
            )
        except Exception as e:
            self._log.error(
                "Failed to send tabular data for ingestion." f"Exception was: {e}"
            )
            errors.log_and_rethrow(
                ResolvableBy.USER_ERROR,
                self._log,
                what_happened="Failed to send tabular data for ingestion",
                why_it_happened=f"Exception was: {e}",
                consequences="Data is not ingested and the method will raise an exception",
                countermeasures="Please look the error message and try to fix the error and re-try.",
                exception=e,
                wrap_in_vdk_error=True,
            )

    def __initialize_ingester(self, method) -> IngesterBase:
        ingester_plugin = None

        try:
            ingester_plugin = self._ingester_builders[method]()
        except KeyError:
            self._log.error("Could not initialize ingestion plugin.")

        if ingester_plugin is None:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
                log=self._log,
                what_happened=f"Could not create new ingester plugin of type {method}.",
                why_it_happened=f"VDK was run with method={method}, however no valid ingester plugin was created.",
                consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
                countermeasures=f"Seems to be a bug in the plugin for method {method}. Make sure it's correctly installed. "
                f"If upgraded recently consider reverting to previous version. Or use another method type.",
            )
        else:
            self._cached_ingesters[method] = IngesterBase(
                self._state.get(ExecutionStateStoreKeys.JOB_NAME),
                self._state.get(CommonStoreKeys.OP_ID),
                ingester_plugin,
                IngesterConfiguration(config=self._cfg),
                True if method in self._pre_processor_sequence else False,
            )

        return self._cached_ingesters[method]

    def close(self):
        """
        Wait for all ingestion payloads to be sent and clean up the queues. This
        method iterates over all ingestion plugins, and blocks the termination of the
        process before all queues are emptied.
        """
        errors_list: Dict = dict()
        for method, ingester in self._cached_ingesters.items():
            try:
                ingester.close()
            except Exception as e:
                errors_list[method] = e
                self._log.warning(
                    f"Closing of ingester for method `{method}` failed. "
                    f"Exception was: {e}"
                )

        if errors_list:
            message = ErrorMessage(
                "Ingesting data failed",
                f"On close some following ingest queues types reported errors:  {list(errors_list.keys())}.",
                f"There were errors while closing ingestion. Exceptions were: {errors_list}.",
                "Some data was partially ingested or not ingested at all.",
                "Follow the instructions in the error messages and log warnings. "
                "Make sure to inspect any errors or warning logs generated"
                "Re-try the job if necessary",
            )

            if any(
                filter(lambda v: isinstance(v, UserCodeError), errors_list.values())
            ):
                raise UserCodeError(message)
            elif any(
                filter(
                    lambda v: isinstance(v, VdkConfigurationError), errors_list.values()
                )
            ):
                raise VdkConfigurationError(message)
            else:
                raise PlatformServiceError(message)
