# singer

<a href="https://pypistats.org/packages/vdk-singer" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-singer.svg" alt="monthly download count for vdk-singer"></a>

The vdk-singer plugin provides an easy way to integrate Singer Taps as data sources within the Versatile Data Kit (VDK).
This allows you to pull data from various external systems that have Singer Taps available and use them seamlessly
within your VDK pipelines.




## Usage

```
pip install vdk-singer
```

### Configuration

(`vdk config-help` is useful command to browse all config options of your installation of vdk)


You can configure the Singer data source via the SingerDataSourceConfiguration class. The configuration options include:

* tap_name: The name of the Singer Tap you are using.
* tap_config: A dictionary containing configuration specific to the Singer Tap.
* tap_auto_discover_schema: A boolean to indicate whether to auto-discover the schema.

```python
config = SingerDataSourceConfiguration(
    tap_name="tap-gitlab",
    tap_config={
        "api_url": "https://gitlab.com/api/v4",
        "private_token": "your_token_here",
        # ... other tap specific configurations
    },
    tap_auto_discover_schema=True,

```

### Example

This will change as we will introduce more user frinedly way of defining sources but currently it looks like this:

```python
from vdk.api.job_input import IJobInput
from vdk.internal.builtin_plugins.ingestion.source.factory import SingletonDataSourceFactory
from vdk.plugin.singer.singer_data_source import SingerDataSourceConfiguration

def run(job_input: IJobInput):
    data_source = SingletonDataSourceFactory().create_data_source("singer-tap")
    config = SingerDataSourceConfiguration(
        tap_name="tap-gitlab",
        tap_config={
            "api_url": "https://gitlab.com/api/v4",
            "private_token": "your_token_here",
            # ... other configurations
        },
        tap_auto_discover_schema=True,
    )
    data_source.connect(config, None)
    # ... rest of the job logic

```

#### List all likely available taps

```shell
vdk singer --list-taps
```

### Build and testing

```
pip install -r requirements.txt
pip install -e .
pytest
```

In VDK repo [../build-plugin.sh](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/build-plugin.sh) script can be used also.


#### Note about the CICD:

.plugin-ci.yaml is needed only for plugins part of [Versatile Data Kit Plugin repo](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins).

The CI/CD is separated in two stages, a build stage and a release stage.
The build stage is made up of a few jobs, all which inherit from the same
job configuration and only differ in the Python version they use (3.7, 3.8, 3.9 and 3.10).
They run according to rules, which are ordered in a way such that changes to a
plugin's directory trigger the plugin CI, but changes to a different plugin does not.
