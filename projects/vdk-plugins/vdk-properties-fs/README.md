This plugin allows vdk-core to read/write properties on the local FS. Mainly for development purposes,
to simplify a use-case with local Properties API usage, that would otherwise require a Control Service instance prerequisite.
For example, to quickly demo a data job that uses a secret, so that secret is quickly stored on the presenter's local FS.

# Usage

Run
```bash
pip install vdk-properties-fs
```

After this, data jobs will be able to read and write properties stored on the local file system.

For example

```python
    def run(job_input: IJobInput):
        my_props = {"key": "value"}
        job_input.set_all_properties(my_props)
        assert job_input.get_all_properties() == my_props
        assert job_input.get_property("key") == "value"
```

# Configuration

To enable the plugin, set "PROPERTIES_DEFAULT_TYPE" to "fs-properties-client".
Run vdk config-help - search for those prefixed with "FS_PROPERTIES_" to see what configuration options are available.

# Testing

Testing this plugin locally requires installing the dependencies listed in vdk-plugins/vdk-properties-fs/requirements.txt

Run
```bash
pip install -r requirements.txt
```
