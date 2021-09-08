# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import cast

from taurus.vdk.builtin_plugins.notification.notification_configuration import (
    NotificationConfiguration,
)
from taurus.vdk.core.config import Configuration


def test_notification():
    notif_cfg = NotificationConfiguration(
        cast(
            Configuration,
            dict(NOTIFICATION_EMAIL_CC_LIST="a@gmail.com ; b@foo.com;c@bar.com;"),
        )
    )

    assert notif_cfg.get_email_cc_list() == ["a@gmail.com", "b@foo.com", "c@bar.com"]
