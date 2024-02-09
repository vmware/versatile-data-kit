# confluence-data-source

**VDK data source plugin for Confluence**

This plugin enables Versatile Data Kit (VDK) users to easily integrate and ingest data from Atlassian Confluence into their data processing jobs. It provides a streamlined way to access Confluence page content, utilizing the Confluence API to fetch pages from specified spaces or across the entire Confluence site. The plugin supports multiple authentication methods and is designed to work seamlessly with VDK, allowing for the configuration-driven ingestion of Confluence data.

## Usage

To use the `vdk-confluence-data-source` plugin, install it using pip:

```
pip install vdk-confluence-data-source
```

### Configuration

Configuration options can be set in VDK by using the `vdk config-help` command, which provides a comprehensive list of all configurable options for your VDK installation. For the `confluence-data-source` plugin, the following configurations are available:

### Configuration

Configuration options for the `confluence-data-source` plugin can be set using VDK's configuration commands. These options allow you to specify the details required to connect to and interact with your Confluence instance. The available configurations are detailed below:

| Name                    | Description                                                                                                                                   | Example Value                                                                                     |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `confluence_url`        | The base URL of your Confluence instance.                                                                                                     | `"https://your-confluence-instance.atlassian.net/wiki"`                                           |
| `space_key`             | The key of the Confluence space from which to fetch content. Leave empty to fetch from all spaces.                                            | `"DEMO"`                                                                                          |
| `username`              | Confluence username for authentication. Required if using username and API token for authentication.                                          | `"user@example.com"`                                                                              |
| `api_token`             | Confluence API token for authentication. Can be used instead of `personal_access_token`.                                                      | `"your_api_token"`                                                                                |
| `personal_access_token` | Confluence personal access token for authentication. Can be used instead of `api_token`.                                                      | `"your_personal_access_token"`                                                                    |
| `oauth2`                | OAuth2 credentials for authentication in dictionary format. Includes keys: 'access_token', 'access_token_secret', 'consumer_key', 'key_cert'. | `{"access_token": "...", "access_token_secret": "...", "consumer_key": "...", "key_cert": "..."}` |
| `cloud`                 | Flag indicating if the Confluence instance is cloud-based.                                                                                    | `True`                                                                                            |
| `confluence_kwargs`     | Additional keyword arguments for the Confluence client.                                                                                       | `{"timeout": 60}`                                                                                 |

**Example usage in configuration:**

```ini
[confluence-data-source-config]
confluence_url = https://your-confluence-instance.atlassian.net/wiki
space_key = DEMO
username = user@example.com
api_token = your_api_token
# personal_access_token = your_personal_access_token
# oauth2 = {"access_token": "token", "access_token_secret": "secret", "consumer_key": "key", "key_cert": "cert"}
cloud = True
# confluence_kwargs = {"timeout": 60}
```

These configurations allow you to tailor the Confluence data source to your specific Confluence instance and authentication method, ensuring secure and efficient access to your Confluence content.
### Example

To use the `confluence-data-source` in a VDK job:

```python
from vdk.plugin.confluence_data_source import ConfluenceDataSource

# Configuration example
config = {
    "confluence_url": "https://your-confluence-instance.atlassian.net/wiki",
    "api_token": "your_api_token",
    "space_key": "DEMO",
}

# Initialize the data source
confluence_data_source = ConfluenceDataSource()
confluence_data_source.configure(config)

# Use the data source in your VDK job
confluence_data_source.connect()
for stream in confluence_data_source.streams():
    for page_content in stream.read():
        print(page_content.data, page_content.metadata)
confluence_data_source.disconnect()
```

### Build and testing

To build and test the `confluence-data-source` plugin, follow these steps:

```
pip install -r requirements.txt
pip install -e .
pytest
```

For plugins that are part of the [Versatile Data Kit Plugin repo](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins), you can also use the `build-plugin.sh` script located in the VDK repo for building and testing:

```
../build-plugin.sh
```

#### Note about the CICD:

For CI/CD, `.plugin-ci.yaml` is required for plugins that are part of the Versatile Data Kit Plugin repository. The CI/CD process is divided into two stages: build and release. Each stage consists of jobs that are configured to run on different Python versions (3.7, 3.8, 3.9, and 3.10), ensuring compatibility. The CI/CD runs according to rules designed to trigger the plugin's CI pipeline when changes are made within its directory.
