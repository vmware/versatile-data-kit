# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pluggy

"""
The plugin project name. IT is used in auto-discovery of the hooks and plugins.
If external module needs to recognize as a plugin module they need to specify this as an entry point.
"""
PROJECT_NAME = "vdk_control_cli.plugin"

"""
Decorator helper class for marking functions as hook specifications.
"""
hookspec = pluggy.HookspecMarker(PROJECT_NAME)

"""
Decorator helper class for marking functions as hook implementations.
The method name must match one of those defined as hookspec
The method signature - the arguments need to be subset of arguments defined in hookspec
"""
hookimpl = pluggy.HookimplMarker(PROJECT_NAME)
