# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pluggy

"""
The plugin project name. It is used in auto-discovery of the hooks and plugins.
If external module needs to recognize as a plugin module they need to specify this as an entry point.
"""
GROUP_NAME = "vdk.plugin.run"

"""
Decorator helper class for marking functions as hook specifications.

The hook spec can be configured using following variables:

If ``firstresult`` is ``True`` the 1:N hook call (N being the number of registered
hook implementation functions) will stop at I<=N when the I'th function
returns a non-``None`` result.

If ``historic`` is ``True`` calls to a hook will be memorized and replayed
on later registered plugins.
"""
hookspec = pluggy.HookspecMarker(GROUP_NAME)

"""
Decorator helper class for marking functions as hook implementations.
The method name must match one of those defined as hookspec
The method signature - the arguments need to be subset of arguments defined in hookspec

If any hookimpl errors with an exception no further callbacks are invoked
and the exception is packaged up and delivered to any wrappers
before being re-raised at the hook invocation point.

Plugin execution order can be configured in the decorator with following variables:

If ``optionalhook`` is ``True`` a missing matching hook specification will not result
in an error (by default it is an error if no matching spec is found).

If ``tryfirst`` is ``True`` this hook implementation will run as early as possible
in the chain of N hook implementations for a specification.

If ``trylast`` is ``True`` this hook implementation will run as late as possible
in the chain of N hook implementations.

If ``hookwrapper`` is ``True`` the hook implementations needs to execute exactly
one ``yield``.  The code before the ``yield`` is run early before any non-hookwrapper
function is run.  The code after the ``yield`` is run after all non-hookwrapper
function have run.  The ``yield`` receives a :py:class:`.callers._Result` object
representing the exception or result outcome of the inner calls (including other
hookwrapper calls).
Example:

@hookimpl(hookwrapper=True)
def func():
    before_other_hooks_execute()
    outcome = yield
    # outcome.excinfo may be None or a (cls, val, tb)
    # outcome.get_result() will raise exception if there was an exception before.
    after_other_hooks_executed(outcome.get_result())
    outcome.force_result(new_res)  # set new return result

For more details see https://pluggy.readthedocs.io

"""
hookimpl = pluggy.HookimplMarker(GROUP_NAME)
