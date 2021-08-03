## Overview

The documentation here is aimed at project developers. <br>
For user facing documentation see [README.md](./README.md).

## Local build

./cicd/build.sh - this will build, run unit tests and setup pre-commit hooks.

## Setup IDE (IntelliJ / PyCharm)

### Importing the project

We recommend using IntelliJ and the Python plugin or PyCharm for development. The steps following assume this.

Setting up the development environment can be done in the following way:
* Clone the repository;
* Open IntelliJ, click `Import Project` and pick the directory where you cloned vdk-core;
* Choose `Create project from existing sources` with default settings, then click `Next`;
* Once you reach the window to pick an SDK click the `+` sign and add Python SDK (you need to install python3.7 and the plugin mentioned above as a prerequisite); in case you have duplication of the venvs, delete the one which does not contain any files;
* In the new window choose `Virtual Environment` and `New environment` - the `Location` field is where the virtual environment will be created;
* For `Base Interpreter` pick the python3.7 location and leave the checks below empty, then finish the import process.

### Setting up the imported project

Once you have imported the project follow the steps to properly resolve the dependencies:
* Navigate to `File | Project Structure` and then to `Project Settings | Modules`;
* You will see `vdk-core` as the only option and pressing it will open the layout of the project;
* Click `src` and above the window click `Sources` to instruct IntelliJ that this is the source folder and then `Apply` and `Ok`;
* We recommend that you install mypy IntelliJ/PyCharm plugin so that you have type checking in IDE.

## Implementing plugins

* You can find a template for implementing plugins in `/plugins/plugin-template`;
* Include your implementation files inside the `/src/taurus/vdk/` directory, and any tests inside the `/tests/` directory;
* Include your dependencies inside the `requirements.txt` file;
* Change the name of the plugin package, the plugin itself and the name of the Python file containing the plugin hooks inside the `setup.py` file;
* Change the name of the build and release jobs and the name variable inside the `.plugin-ci.yml` file to match the name of your plugin;
* Plugins CI/CD installs the latest released vdk-core version, so if you've made plugin changes which depend on vdk-core
  changes, you should first bump the vdk-core version (version.txt) and merge the vdk-core changes, so that the
  next merge request (containing your plugin changes) will use your vdk-core changes.

## Tests

Tests are run with pytest.
To run them inside IntelliJ IDE see [pytest.html](https://www.jetbrains.com/help/pycharm/pytest.html) <br>
In short:
* Open the Settings/Preferences | Tools | Python Integrated Tools settings dialog as described in Choosing Your Testing Framework;
* In the Default test runner field select pytest;
* Click OK to save the settings;
*  Add tests directory as Test Sources;

* Testing the `vdk-trino` plugin locally requires a manually started trino. You can do this by running:
```bash
docker run -p 8080:8080 --name trino trinodb/trino
```


## Release

Releases are made to PyPI. <br>
Versioning follows https://semver.org.

* A release step in Gitlab CI is automatically triggered after merging changes if build/tests are successful.
* Update CHANGELOG.md (for major or minor version updates).
