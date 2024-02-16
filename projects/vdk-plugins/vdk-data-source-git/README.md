# data-source-git

<a href="https://pypistats.org/packages/vdk-data-source-git" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-data-source-git.svg" alt="monthly download count for vdk-data-source-git"></a>

Extracts content from Git repositories along with associated file metadata.

## Usage

```
pip install vdk-data-source-git
```

### Extracted Data Schema

The extracted data is returned in a `DataSourcePayload` object with two main components: `content` and `metadata`.

#### `content`

The `content` field contains the actual content of the file as a string.

#### `metadata`

The `metadata` field contains a dictionary with the following schema:

| Key                    | Description                                       | Data Type | Example       |
|------------------------|---------------------------------------------------|-----------|---------------|
| `size`                 | The size of the file in bytes                     | Integer   | 12345         |
| `path`                 | The path of the file in the repository            | String    | "src/main.py" |
| `num_lines`            | The number of lines in the file                   | Integer   | 678           |
| `file_extension`       | The file extension                                | String    | ".py"         |
| `programming_language` | The detected programming language of the file     | String    | "Python"      |
| `is_likely_test_file`  | Flag indicating if the file is likely a test file | Boolean   | false         |

### Configuration

(`vdk config-help` is useful command to browse all config options of your installation of vdk)

| Name    | Description                              | (example)  Value               |
|---------|------------------------------------------|--------------------------------|
| git_url | URL of the Git repository to be cloned.	 | "https://github.com/user/repo" |


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
