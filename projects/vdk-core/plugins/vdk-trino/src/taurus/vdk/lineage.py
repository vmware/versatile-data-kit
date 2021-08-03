# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from abc import ABC
from typing import Any
from typing import Dict


class LineageLogger(ABC):
    """
    This interface describes what behaviour a lineage logger must possess to interact with the lineage logging
    functionality afforded by vdk-trino.
    """

    def send(
        self, lineage_data: Dict[str, Any]
    ) -> None:  # TODO: implement a common lineage data standard
        """
        This method sends the collected lineage data to some lineage data processing application.

        :param lineage_data: The collected lineage data.
        """
        pass
