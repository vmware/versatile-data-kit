This plugin allows vdk-core to access vdk-control-cli functionality.

Upon installing it enhances vdk with CLI commands for data job lifecycle management available from vdk-control-cli package

It will also install properties plugin and switch Properties in vdk to use Control Service Properties API.
By default no Properties backend is used otherwise.

# Usage


```bash
pip install vdk-plugin-control-cli
```

### New CLI commands

Then on the vdk CLI you should be able to see the new commands. Run
```bash
vdk --help
```
and you will see extra commands being added:
```
Commands:
  ...
  login                  Authentication against the Control Service.
  logout                 Logout the user from the Data Jobs Service by...
  create                 Creates a new data job in cloud and locally.
  delete                 Deletes a data job from the cloud.
  deploy                 Deploys a data job.
  ...
```

And you can use them from the same CLI `vdk`

### New properties backend client registered

You can now access remote properties from Control Service Properties API
Store state, configuration or secrets there using CLI or Python JobInput API

For example, let's store some api-uri

```bash
vdk properties --set 'api-uri' 'http://cool.cool.api.com'
```

and then we can use it in our data job

```python
def run(job_input: IJobInput):
    uri = job_input.get_property('api-uri')
    print(requests.get(uri))
```

# Build

The easiest way is to use the ../build-plugin.sh helper script

```bash
../build-plugin.sh
```
