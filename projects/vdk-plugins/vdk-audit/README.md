## Versatile Data Kit Audit Plugin

<a href="https://pypistats.org/packages/vdk-audit" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-audit.svg" alt="monthly download count for vdk-audit"></a>

Visibility into the actions provides opportunities for test frameworks, logging
frameworks, and security tools to monitor and optionally limit actions taken by the
runtime.
This plugin provides an ability to audit and potentially limit user operations.
These operations are typically deep within the Python runtime or standard library, such
as dynamic code compilation, module imports or OS command invocations. In order to have a
better understanding of what exactly the job does, we will log all job operations.

### Usage

To use the plugin, just install it using

```bash
pip install vdk-audit
```
