# Incremental Ingestion using Job Properties - Colab Notebook

This folder contains a Google Colab notebook that demonstrates incremental ingestion from a local SQLite database using Versatile Data Kit (VDK).

## Overview

The notebook provides an interactive tutorial on how to:
- Use VDK's job properties to track state between job runs
- Perform incremental ingestion (only ingesting new/changed records)
- Configure VDK for SQLite database connections
- Use VDK's IPython extension in a notebook environment

## Contents

- `incremental-ingest-example-notebook.ipynb` - The Google Colab notebook with step-by-step instructions

## Usage

### Option 1: Run on Google Colab (Recommended)

Click the "Open in Colab" badge at the top of the notebook to run it directly in Google Colab without any local setup.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vmware/versatile-data-kit/blob/main/examples/incremental-ingest-from-db-example-notebook/incremental-ingest-example-notebook.ipynb)

### Option 2: Run Locally

1. Install dependencies:
   ```bash
   pip install vdk-ipython vdk-sqlite vdk-ingest-http
   ```

2. Open the notebook in Jupyter:
   ```bash
   jupyter notebook incremental-ingest-example-notebook.ipynb
   ```

## What You'll Learn

1. How to set up a source SQLite database with sample data
2. How to configure VDK environment variables for database connections
3. How to use the `%%vdksql` magic command for SQL operations
4. How to implement incremental ingestion using job properties
5. How to use `job_input.get_property()` and `job_input.set_all_properties()`
6. How to ingest tabular data using `send_tabular_data_for_ingestion()`

## Key Concepts

### Incremental Ingestion

Incremental ingestion is a pattern where only new or changed records are processed, rather than reloading the entire dataset each time. This is achieved by:

- Storing a "watermark" (like the last processed date) in job properties
- Querying only records newer than the watermark
- Updating the watermark after successful ingestion

### Job Properties

VDK provides a key-value store for persisting state between job runs:

- `get_property(key, default_value)` - Retrieve a property value
- `set_all_properties(dict)` - Store multiple property values

## Related Resources

- [Original Example (File-based)](https://github.com/vmware/versatile-data-kit/tree/main/examples/incremental-ingest-from-db-example)
- [VDK Wiki - Job Properties](https://github.com/vmware/versatile-data-kit/wiki/Job-Properties)
- [VDK Wiki - Getting Started](https://github.com/vmware/versatile-data-kit/wiki/Getting-Started)
- [Issue #3060](https://github.com/vmware/versatile-data-kit/issues/3060) - This notebook addresses this issue

## Contributing

This notebook was created as part of the [Google Colab Notebooks for VDK Examples](https://github.com/vmware/versatile-data-kit/milestone/29) milestone.

See the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines.
