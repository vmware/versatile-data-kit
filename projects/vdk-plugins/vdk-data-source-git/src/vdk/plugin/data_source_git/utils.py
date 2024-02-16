# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound


def is_test_file(file_path: str) -> bool:
    return "test" in file_path


def detect_language(file_path: str) -> str:
    try:
        lexer = get_lexer_for_filename(file_path)
        return lexer.name
    except ClassNotFound:
        return "Unknown"
