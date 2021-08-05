This plugin provides utility tools used for the testing of vdk-core and vdk-core plugins.

# Usage

### CliEntryBasedTestRunner

CliEntryBasedTestRunner provides an easy way to create unit or functional tests for your plugins in isolated environment.
Similarly this can be used to unit tests data jobs.

For example , let's say we want to test newly developed AtlasLineagePlugin

```python
db_plugin = AtlasLineagePlugin()
# we pass the plugin to the runner that will make sure to register it
runner = CliEntryBasedTestRunner(db_plugin)

# and then invoke the command we want to test -
# in this case data job run
result: Result = runner.invoke(
    [ "run", util_funcs.jobs_path_from_caller_directory("simple-create-insert") ]
)

cli_assert_equal(0, result)
assert 'expected_schema' in result.output
```

### Testing plugins

Some useful plugins that can be used during testing can be seen in util_plugins.
