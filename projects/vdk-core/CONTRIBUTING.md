## Overview

The documentation here is aimed at project developers. <br>
For user facing documentation see [README.md](./README.md).

## Local build

./cicd/build.sh - this will build, run unit tests and setup pre-commit hooks.

## Setup IDE (IntelliJ / PyCharm)

We recommend using IntelliJ and the Python plugin or PyCharm for development. The steps following assume this.

Setting up the development environment can be done in the following way:
* Clone the repository;
* Import the project in your IDE (pick the directory where you cloned vdk-core);
* Set the project's Python interpreter - either create or choose an existing project-specific virtual environment with python3.7 or newer;
* Mark vdk-core/src and vdk-core/tests as Sources in order to instruct your IDE that they are the source folders of the project;
* We recommend that you install mypy IntelliJ/PyCharm plugin so that you have type checking in the IDE.

## Implementing plugins

* You can find a template for implementing plugins in `projects/vdk-plugins/plugin-template`;
* Include your implementation files inside the `/src/vdk/internal/` directory, and any tests inside the `/tests/` directory;
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


## Release

Releases are made to PyPI. <br>
Versioning follows https://semver.org.

* A release step in Gitlab CI is automatically triggered after merging changes if build/tests are successful.
* Update CHANGELOG.md (for major or minor version updates).
