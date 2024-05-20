# Copyright 2024-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0


class DataQualityException(Exception):
    """
    Exception raised for errors with the quality of the data.

    Attributes:
        checked_object -- Object that the quality checks are ran against
        target_table -- DWH table where target data is loaded
        source_view -- View from which the raw data is loaded from
    """

    def __init__(self, checked_object, target_table, source_view):
        self.checked_object = checked_object
        self.target_table = target_table
        self.source_view = source_view
        self.message = f"""What happened: Error occurred while performing quality checks.\n
        Why it happened: Object: {checked_object} is not passing the quality checks.\n
        Consequences: The source view data will not be processed to the target table - {target_table}.\n
        Countermeasures: Check the source view: {source_view} what data is trying to be processed."""
        super().__init__(self.message)
