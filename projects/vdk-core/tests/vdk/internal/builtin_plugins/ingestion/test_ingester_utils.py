# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime
import json
from decimal import Decimal

from pytest import raises
from vdk.internal.builtin_plugins.ingestion.ingester_utils import IngesterJsonEncoder


def test_ingester_json_encoder():
    payload_no_specials = {"a": 1, "b": 2}
    payload_with_decimal = {"a": Decimal(1), "b": Decimal(2)}
    payload_with_datetime = {
        "a": datetime.datetime.fromtimestamp(1700641925),
        "b": datetime.datetime.fromtimestamp(1700641925),
    }
    payload_with_bytes = {
        "a": b"enoded string bla bla",
        "b": b"another encoded string, look at me, I'm so special",
    }

    assert json.dumps(payload_no_specials) == '{"a": 1, "b": 2}'

    with raises(TypeError):
        json.dumps(payload_with_decimal)

    with raises(TypeError):
        json.dumps(payload_with_datetime)

    with raises(TypeError):
        json.dumps(payload_with_bytes)

    assert (
        json.dumps(payload_no_specials, cls=IngesterJsonEncoder) == '{"a": 1, "b": 2}'
    )

    assert (
        json.dumps(payload_with_decimal, cls=IngesterJsonEncoder)
        == '{"a": 1.0, "b": 2.0}'
    )

    assert (
        json.dumps(payload_with_datetime, cls=IngesterJsonEncoder)
        == '{"a": 1700641925.0, "b": 1700641925.0}'
    )

    assert json.dumps(payload_with_bytes, cls=IngesterJsonEncoder) == (
        '{"a": [101, 110, 111, 100, 101, 100, 32, 115, 116, 114, 105, 110, 103, 32, '
        '98, 108, 97, 32, 98, 108, 97], "b": [97, 110, 111, 116, 104, 101, 114, 32, '
        "101, 110, 99, 111, 100, 101, 100, 32, 115, 116, 114, 105, 110, 103, 44, 32, "
        "108, 111, 111, 107, 32, 97, 116, 32, 109, 101, 44, 32, 73, 39, 109, 32, 115, "
        "111, 32, 115, 112, 101, 99, 105, 97, 108]}"
    )
