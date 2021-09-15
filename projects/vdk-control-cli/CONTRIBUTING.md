What follows are only additions to above. <br>

The documentation here is aimed at developers of the project. <br>
For user facing documentation see [README.md](./README.md)

The CLI follows 12 factor CLI Apps principles:
https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46

## Build

Make sure you have python3 installed. It's strongly recommended to use virtual environment.
It's also recommended to use python installer like pyenv or conda. The writer of this recommends pyenv.
See [here to install pyenv](https://github.com/pyenv/pyenv#installation) and [here to install pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv#installation)

CICD is managed through [gitlab-ci.yml](./.gitlab-ci.yml). You can see how to build, run tests, deploy there best.

Use `cicd/build.sh` script to build.
It will run tests install pre-commit hooks
(see pre-commit-config.yaml file for details )
and install the CLI in editable mode (pip install -e)

## Setup IDE (IntelliJ / PyCharm)

### Importing the project

For developing we use IntelliJ with [python plugin](https://plugins.jetbrains.com/plugin/631-python) (or PyCharm) and python 3.7+ so make sure you have both installed as prerequisite.

Setting up the environment involves:
* Clone repository
* Open IntelliJ and click Import Project and pick directory where you cloned vdk-control-cli
* Chose Create project from existing sources with default settings then click `Next`
* Once you reach the window to pick SDK click the `+` sign and add Python SDK (you need to install python3.7 and the plugin) mentioned above as a prerequisite. In case you have duplication of the venvs, delete the one which does not contain any files.
* On that new window chose `Virtual Environment` and `New environment`
* The `Location` field is where the virtual environment will be created. Default is the vdk-control-cli directory, so append `/venv` to the default value.
* On `Base Interpreter` pick python3.7 location and leave the checks below empty then finish the import process

### Setting up the imported project

Once you have imported the project follow the steps to properly resolve dependencies:
* Navigate to File | Project Structure and then navigate to Project Settings | Modules
* You will see `vdk-control-cli` as the only option and pressing it will open the layout of the project
* Click the `src` and above the window click `Sources` to instruct IntelliJ that this is the source folder and then `Apply` and `Ok`

## Install dependencies

In order to install dependencies open terminal in IntelliJ:
* Activate the virtual environment
* Run `pip install --upgrade pip && pip install -r requirements.txt`
> Note: we are doing this manually since the `--extra-index-url` to install the sdk is not supported by python plugin for IntelliJ


## Tests

Tests are run with pytest
To run them inside IntelliJ IDE see [pytest.html](https://www.jetbrains.com/help/pycharm/pytest.html) <br>
In short
* Open the Settings/Preferences | Tools | Python Integrated Tools settings dialog as described in Choosing Your Testing Framework.
* In the Default test runner field select pytest.
* Click OK to save the settings.

In case IntelliJ still runs tests with `Unittest` you can edit configuration the following way:
* In the upper corner of the environment there is configuration which will say `Unittests in tests`
* Press this window and `Edit configuration`
* Press `+` and Python tests | pytest
* By default you should have `Use specified interpreter` if not chose this option. It should point to the venv directory configured above
* Delete the `Unittests in python` so its not used by default and `Apply` and `Ok`

If you click right button on the `tests` folder you should now see `Run 'pytest in tests'` instead of the Unittests option.

## Release

Release means it's uploaded in PIP Repository. <br>
Versioning follows https://semver.org

The CI would set automatically patch version and make new release on each commit to main with successful CI Pipeline.

* To bump major or minor version edit [version.txt](./version.txt)
* [CHANGELOG.md](./CHANGELOG.md) should be updated when the change is introduced. When major or minor version is bumped, create new section for it only.

## Running VDK CLI locally

You can use one of the following installations to run VDK CLI locally:
* install it in an editable mode (from root of project)
```bash
pip install -e .
```
