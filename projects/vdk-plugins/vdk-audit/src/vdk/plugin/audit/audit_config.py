# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import ConfigurationBuilder

AUDIT_HOOK_ENABLED = "AUDIT_HOOK_ENABLED"
AUDIT_HOOK_FORBIDDEN_EVENTS_LIST = "FORBIDDEN_EVENTS_LIST"
AUDIT_HOOK_EXIT_ON_FORBIDDEN_EVENT = "EXIT_ON_FORBIDDEN_EVENT"
AUDIT_HOOK_EXIT_CODE = "EXIT_CODE"
AUDIT_HOOK_FORBIDDEN_EVENTS_LIST_DEFAULT = (
    "os.system;os.chdir;os.chflags;os.chown;os.fork;"
    "os.forkpty;os.getxattr;os.kill;os.killpg;os.link;os.listxattr;"
    "os.lockf;os.posix_spawn;os.putenv;os.removexattr;os.rmdir;"
    "os.setxattr;os.spawn;os.startfile;os.symlink;"
    "os.truncate;os.unsetenv;pty.spawn;os.spawn;"
    "os.posix_spawn;subprocess.run"
)


class AuditConfiguration:
    def __init__(self, config):
        self.__config = config

    def enabled(self):
        return self.__config.get_value(AUDIT_HOOK_ENABLED)

    def forbidden_events_list(self):
        return self.__config.get_value(AUDIT_HOOK_FORBIDDEN_EVENTS_LIST)

    def exit_code(self):
        return self.__config.get_value(AUDIT_HOOK_EXIT_CODE)

    def exit_on_forbidden_event(self):
        return self.__config.get_value(AUDIT_HOOK_EXIT_ON_FORBIDDEN_EVENT)


def add_definitions(config_builder: ConfigurationBuilder) -> None:
    config_builder.add(
        key=AUDIT_HOOK_ENABLED,
        default_value=True,
        description="Set to false if you want to disable audit hook plugin entirely.",
    )
    config_builder.add(
        key=AUDIT_HOOK_FORBIDDEN_EVENTS_LIST,
        default_value=AUDIT_HOOK_FORBIDDEN_EVENTS_LIST_DEFAULT,
        description="List of forbidden user operations. These operations are "
        "typically deep within the Python runtime or standard library, "
        "such as dynamic code compilation, module imports or OS command "
        "invocations. "
        "The field accepts semi-colon separated values. "
        "Example: 'os.removexattr;os.rename;os.rmdir;os.scandir'",
    )
    config_builder.add(
        key=AUDIT_HOOK_EXIT_ON_FORBIDDEN_EVENT,
        default_value=True,
        description="If it is true, the data job will be fully terminated on forbidden "
        "operation - no cleanup, no per-attempt notifications, etc. "
        "If it is false, the termination of data job on forbidden "
        "operation will be disabled.",
    )
    config_builder.add(
        key=AUDIT_HOOK_EXIT_CODE,
        default_value=0,
        description="If AUDIT_HOOK_EXIT_ON_FORBIDDEN_EVENT is true, "
        "the data job will be fully terminated on forbidden operation "
        "with the exit code defined via this field.",
    )
