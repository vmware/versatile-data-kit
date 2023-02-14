# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import cast

from vdk.internal.builtin_plugins.notification.notification_configuration import (
    NotificationConfiguration,
)
from vdk.internal.core.config import Configuration


def test_notification():
    notif_cfg = NotificationConfiguration(
        cast(
            Configuration,
            dict(NOTIFICATION_EMAIL_CC_LIST="a@gmail.com ; b@foo.com;c@bar.com;"),
        )
    )

    assert notif_cfg.get_email_cc_list() == ["a@gmail.com", "b@foo.com", "c@bar.com"]
