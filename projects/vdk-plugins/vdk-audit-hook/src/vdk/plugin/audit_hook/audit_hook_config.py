# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import ConfigurationBuilder

AUDIT_HOOK_ENABLED = "AUDIT_HOOK_ENABLED"
NOT_PERMITTED_EVENTS_LIST = "NOT_PERMITTED_EVENTS_LIST"
EXIT_ON_NOT_PERMITTED_EVENT = "EXIT_ON_NOT_PERMITTED_EVENT"
NOT_PERMITTED_EVENTS_LIST_DEFAULT = (
    "os.system;os.chdir;os.chflags;os.chmod;os.chown;os.fork;"
    "os.forkpty;os.getxattr;os.kill;os.killpg;os.link;os.listxattr;"
    "os.lockf;os.posix_spawn;os.putenv;os.removexattr;os.rmdir;"
    "os.scandir;os.setxattr;os.spawn;os.startfile;os.symlink;"
    "os.truncate;os.unsetenv;os.utime;pty.spawn"
)


class AuditHookConfiguration:
    def __init__(self, config):
        self.__config = config

    def enabled(self):
        return self.__config.get_value(AUDIT_HOOK_ENABLED)

    def not_permitted_events_list(self):
        return self.__config.get_value(NOT_PERMITTED_EVENTS_LIST)

    def exit_on_not_permitted_event(self):
        return self.__config.get_value(EXIT_ON_NOT_PERMITTED_EVENT)


def add_definitions(config_builder: ConfigurationBuilder) -> None:
    config_builder.add(
        key=AUDIT_HOOK_ENABLED,
        default_value=True,
        description="Set to false if you want to disable audit hook plugin entirely.",
    )
    config_builder.add(
        key=NOT_PERMITTED_EVENTS_LIST,
        default_value=NOT_PERMITTED_EVENTS_LIST_DEFAULT,
        description="List of NOT permitted actions.",
    )
    config_builder.add(
        key=EXIT_ON_NOT_PERMITTED_EVENT,
        default_value=True,
        description="Set to false if you want to disable termination of data job on not permitted action.",
    )
