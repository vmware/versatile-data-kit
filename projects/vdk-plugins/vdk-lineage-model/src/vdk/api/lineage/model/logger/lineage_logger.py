# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from abc import ABC
from abc import abstractmethod

from vdk.api.lineage.model.sql.model import LineageData


class ILineageLogger(ABC):
    """
    This interface describes what behaviour a lineage logger implementation must possess in order to interact with
    lineage logging functionality offered by other vdk plugins that support emitting lineage data.
    """

    @abstractmethod
    def send(self, lineage_data: LineageData) -> None:
        """
        This method sends the collected lineage data to some lineage data processing application.

        :param lineage_data: The collected lineage data.
        """
        pass
