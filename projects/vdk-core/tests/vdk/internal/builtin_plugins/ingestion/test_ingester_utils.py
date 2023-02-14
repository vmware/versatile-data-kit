# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
from decimal import Decimal

from pytest import raises
from vdk.internal.builtin_plugins.ingestion.ingester_utils import DecimalJsonEncoder


def test_decimal_json_encoder():
    payload_no_decimal = {"a": 1, "b": 2}
    payload_with_decimal = {"a": Decimal(1), "b": Decimal(2)}

    assert json.dumps(payload_no_decimal) == '{"a": 1, "b": 2}'

    with raises(TypeError):
        json.dumps(payload_with_decimal)

    assert json.dumps(payload_no_decimal, cls=DecimalJsonEncoder) == '{"a": 1, "b": 2}'

    assert (
        json.dumps(payload_with_decimal, cls=DecimalJsonEncoder)
        == '{"a": 1.0, "b": 2.0}'
    )
