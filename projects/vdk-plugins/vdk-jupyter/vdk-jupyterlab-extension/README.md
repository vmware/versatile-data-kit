# vdk-jupyterlab-extension

A Jupyterlab extension for using VDK
For more information see: https://github.com/vmware/versatile-data-kit/tree/main/specs/vep-994-jupyter-notebook-integration

This extension is composed of a Python package named `vdk-jupyterlab-extension`
for the server extension and a NPM package named `vdk-jupyterlab-extension` for the frontend extension.

## Requirements

- JupyterLab >= 3.0
- python ~=3.7
- Versatile Data Kit
- npm

## Install and run

```bash
# install the extension
pip install vdk-jupyterlab-extension
# run jupyterlab
jupyter lab
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall vdk-jupyterlab-extension
```

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

If you are struggling with a particular aspect of the JupyterLab API,
you can contact the Jupyter team in the following way: go to their repo issues page at
https://github.com/jupyterlab/jupyterlab/issues/new/choose
then click on Open in the "Chat with the devs" section, which will send you
to a Gitter channel where you can ask your question.

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
../cicd/build.sh
```

NB: If you're changing some dependencies of the project,
meaning you're adding, removing, or updating packages, you'd use npm install.

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
# Server extension must be manually disabled in develop mode
jupyter server extension disable vdk-jupyterlab-extension
pip uninstall vdk-jupyterlab-extension
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `vdk-jupyterlab-extension` within that folder.

### Front-end extension
This extension uses [JSX](https://reactjs.org/docs/introducing-jsx.html).

The components of the front-end extension are located in the /src directory. All the new UI elements are added there.

The main script for the extension is index.ts - this is where the front-end extension is loaded.
In handlers.ts the connection with the server is done, while in serverRequests.ts all the requests are sent.
In the subdirectory /components are located the JSX components that represent VDK menu elements.
In the subdirectory /dataClasses are located the data classes responsible for saving the user input data for all the
vdk operations.


### Server extension
This extension uses [Tordnado](https://www.tornadoweb.org/en/stable/).

All the requests handlers are located in handlers.py file where the communication with the front-end is created.

The connection with VDK is done in the vdk_ui.py file - all the vdk operations are handled there.

### Job data model
Follows the enum VdkOption from [vdk_options.py](vdk_jupyterlab_extension/vdk_options/vdk_options.py).

In the front-end extension a global storage object (jobData), which holds the information about the current job, is present.
It holds key value pairs, it's keys are generated automatically from the [enum](src/vdkOptions/vdk_options.ts)
and the values of the keys are changed during vdk operations and after the operation ends they need to be set back to default.

For example, if we want to run a job we would set job path and arguments  as:
jobData.set(VdkOption.PATH, value) and jobData.set(VdkOption.ARGUMENTS, value) and after the operation has passed
the values should be set back to default using setJobDataToDefault() function.

Every Jupyter instance has its own global storage object (jobData) that can only be changed from that instance.
When a new Jupyter instance is loaded its jobData is set to default.

The [enum](src/vdkOptions/vdk_options.ts) is generated automatically from  [the python enum](vdk_jupyterlab_extension/vdk_options/vdk_options.py)
and shall not be changed directly in the .ts file. All the changes must be done in the python file and the .ts file will be automatically reloaded.


The front-end sends the data from jobData to the server extension in JSON format.
In the server extension the JSON is loaded as input_data and the specific data can be accessed
via the [enum](vdk_jupyterlab_extension/vdk_options/vdk_options.py).
For example, input_data[VdkOption.NAME.value] would return current job's name.

### Testing the extension

#### Server tests

This extension is using [Pytest](https://docs.pytest.org/) for Python code testing.

Install test dependencies (needed only once):

```sh
pip install -e ".[test]"
```

To execute them, run:

```sh
pytest -vv -r ap --cov vdk-jupyterlab-extension
```

#### Frontend tests

This extension is using [Jest](https://jestjs.io/) for JavaScript code testing.

To execute them, execute:

```sh
jlpm
jlpm test
```

#### Integration tests

This extension uses [Playwright](https://playwright.dev/docs/intro/) for the integration tests (aka user level tests).
More precisely, the JupyterLab helper [Galata](https://github.com/jupyterlab/jupyterlab/tree/master/galata) is used to handle testing the extension in JupyterLab.

More information are provided within the [ui-tests](./ui-tests/README.md) README.
