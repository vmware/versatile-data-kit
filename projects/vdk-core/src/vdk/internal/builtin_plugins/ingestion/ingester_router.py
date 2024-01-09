# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from vdk.api.job_input import IIngester
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.api.plugin.plugin_input import IIngesterRegistry
from vdk.internal.builtin_plugins.ingestion.ingester_base import IngesterBase
from vdk.internal.builtin_plugins.ingestion.ingester_configuration import (
    IngesterConfiguration,
)
from vdk.internal.builtin_plugins.run.execution_state import ExecutionStateStoreKeys
from vdk.internal.core import errors
from vdk.internal.core.config import Configuration
from vdk.internal.core.errors import PlatformServiceError
from vdk.internal.core.errors import ResolvableBy
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.errors import VdkConfigurationError
from vdk.internal.core.statestore import CommonStoreKeys
from vdk.internal.core.statestore import StateStore
from vdk.internal.util.utils import parse_config_sequence

IngesterPluginFactory = Callable[[], IIngesterPlugin]

log = logging.getLogger(__name__)


class IngesterRouter(IIngesterRegistry, IIngester):
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
        method, target = self.__get_correct_method_and_target(method, target)
        self._log.info(
            "Sending object for ingestion with "
            f"method: {method} and target: {target}"
        )

        ingester = self.__get_ingester(method)

        self.__ingest_object(
            ingester=ingester,
            payload=payload,
            destination_table=destination_table,
            method=method,
            target=target,
            collection_id=collection_id,
        )

    def __get_ingester(self, method: str) -> IngesterBase:
        if method in self._cached_ingesters.keys():
            return self._cached_ingesters.get(method)
        elif method in self._ingester_builders.keys():
            return self.__initialize_ingester(method=method)
        else:
            errors.report_and_throw(
                VdkConfigurationError(
                    f"Provided method, {method}, has invalid value."
                    f"VDK was run with method={method}, however {method} is not part of the available ingestion methods."
                    f"Provide either valid value for method, or install ingestion plugin that supports this type. "
                    f"Currently possible values are {list(self._ingester_builders.keys())}"
                )
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
        method, target = self.__get_correct_method_and_target(method, target)
        self._log.info(
            "Sending tabular data for ingestion with "
            f"method: {method} and target: {target}"
        )

        ingester = self.__get_ingester(method)
        self.__ingest_tabular_data(
            ingester=ingester,
            rows=rows,
            column_names=column_names,
            destination_table=destination_table,
            method=method,
            target=target,
            collection_id=collection_id,
        )

    def __get_correct_method_and_target(self, method, target):
        # Use the method and target provided by customer, or load the
        # default ones, if set. `method` and `target` provided when the
        # method is called take precedence over the ones set with
        # environment variables.
        method = method or self._cfg.get_value("INGEST_METHOD_DEFAULT")
        method = method.lower() if method is not None else None
        target = target or self._cfg.get_value("INGEST_TARGET_DEFAULT")
        return method, target

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
            errors.report(ResolvableBy.USER_ERROR, e)
            raise

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
            errors.report(ResolvableBy.USER_ERROR, e)
            raise

    def __initialize_ingester(self, method) -> IngesterBase:
        ingester_plugin = None

        try:
            ingester_plugin = self._ingester_builders[method]()
        except KeyError:
            self._log.error("Could not initialize ingestion plugin.")

        if ingester_plugin is None:
            errors.report_and_throw(
                VdkConfigurationError(
                    f"Could not create new ingester plugin of type {method}.",
                    f"VDK was run with method={method}, however no valid ingester plugin was created.",
                    f"Seems to be a bug in the plugin for method {method}. Make sure it's correctly installed. "
                    f"If upgraded recently consider reverting to previous version. Or use another method type.",
                )
            )
        else:
            # Initialize the pre- and post- processors.
            initialized_pre_processors = self.__get_initialized_processors(
                "INGEST_PAYLOAD_PREPROCESS_SEQUENCE"
            )
            initialized_post_processors = self.__get_initialized_processors(
                "INGEST_PAYLOAD_POSTPROCESS_SEQUENCE"
            )

            self._cached_ingesters[method] = IngesterBase(
                self._state.get(ExecutionStateStoreKeys.JOB_NAME),
                self._state.get(CommonStoreKeys.OP_ID),
                ingester_plugin,
                IngesterConfiguration(config=self._cfg),
                pre_processors=initialized_pre_processors,
                post_processors=initialized_post_processors,
            )

        return self._cached_ingesters[method]

    def __get_initialized_processors(self, config_var: str) -> List:
        return [
            self.__initialize_processor(i)
            for i in parse_config_sequence(self._cfg, key=config_var, sep=",")
        ]

    def __initialize_processor(self, method) -> Optional[IIngesterPlugin]:
        processor_plugin = None

        try:
            processor_plugin = self._ingester_builders[method]()
        except KeyError:
            self._log.error("Could not initialize processor plugin.")

        if processor_plugin is None:
            errors.report_and_throw(
                VdkConfigurationError(
                    "Could not create new processor plugin of method: " f"{method}.",
                    f"Currently possible processor methods are {list(self._ingester_builders.keys())}. "
                    "Make sure the processing configuration value are correct and the plugin is installed. ",
                )
            )
        return processor_plugin

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
            # TODO: Remove the error types
            error_message_lines = [
                "Ingesting data failed",
                f"On close some following ingest queues types reported errors:  {list(errors_list.keys())}.",
                f"There were errors while closing ingestion. Exceptions were: {errors_list}.",
                "Some data was partially ingested or not ingested at all.",
            ]

            if any(
                filter(lambda v: isinstance(v, UserCodeError), errors_list.values())
            ):
                raise UserCodeError(*error_message_lines)
            elif any(
                filter(
                    lambda v: isinstance(v, VdkConfigurationError), errors_list.values()
                )
            ):
                raise VdkConfigurationError(*error_message_lines)
            else:
                error = PlatformServiceError(*error_message_lines)
                raise error
