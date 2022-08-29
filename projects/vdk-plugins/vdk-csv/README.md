## Versatile Data Kit CSV Plugin

This plugin provides functionality to ingest and export CSV files.

### Usage

To use the plugin, just install it using

```bash
pip install vdk-csv
```

Then run help to see what you can do.
```bash
vdk ingest-csv --help
```
and
```bash
vdk export-csv --help
```

For example you can ingest CSV file into tables, or export the result of an executed query to a cvs file.

The ingestion destination depends on how vdk has been configured.
See vdk config-help - search for "ingest" to check for possible ingestion configurations.
