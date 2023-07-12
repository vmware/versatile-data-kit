# VDK Smarter

Making VDK smarter by employing ML/AI.



## Usage

```
pip install vdk-smarter
```

### Configuration

(`vdk config-help` is useful command to browse all config options of your installation of vdk)


### Example

TODO# VDK Smarter

Making VDK smarter by employing ML/AI.



## Usage

```
pip install vdk-smarter
```

### Configuration

(`vdk config-help` and search for configuration starting with "openai")

### Example

By default reviews are disabled since they are expensive.

To enable you need to set `openai_review_enabled` to `true` in the configuration and `openai_api_key`.
You can see `vdk config-help` (search for configuration with openai prefix) for more information.

Once enabled on vdk run each query statement executed will be also reviewed and scored.

```
vdk run example
```
```bash
Query:
CREATE TABLE IF NOT EXISTS super_collider.example_table(
   vc_id STRING,
   esx_id STRING,
   vm_count INT
) STORED AS PARQUET;


Review:
  {
    "score": 5,
    "review": "No further changes needed. The query is efficient, readable, and follows best practices.
               There are no potential errors, optimization, or security vulnerabilities."}

...
Query:
CREATE TABLE IF NOT EXISTS super_collider.example_fact_snapshot(
                  vc_id STRING,
                  esx_count BIGINT,
                  vm_count BIGINT
) STORED AS PARQUET;


Review:
{"score": 4, "review": "The query is well-structured and follows best practices.
                        However, there is an opportunity to improve its readability by
                        adding comments to explain the purpose of the query  and the meaning of the parameters.
                        Additionally, there is potential to optimize the query by providing more precise column types."}
```

At the end a report is generated `queries_reviews_report.md` with all the queries and their reviews.

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
