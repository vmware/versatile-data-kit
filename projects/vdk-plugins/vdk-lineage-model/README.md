# VDK Lineage Model

<a href="https://pypistats.org/packages/vdk-lineage-model" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-lineage-model.svg" alt="monthly download count for vdk-lineage-model"></a>

VDK Lineage Model plugin aims to abstract emitting lineage data from VDK data jobs, so that different lineage loggers
can be configured at run time in any plugin that supports emitting lineage data.
The plugin describes the lineage data model and an interface for loggers that are responsible to send the lineage
information to the desired system.

At POC level currently. Breaking changes should be expected.

TODOs:
 - Describe Non-SQL lineage (ingest, load data,etc)
 - Extend support for all query types
