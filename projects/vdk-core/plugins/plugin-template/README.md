This directory outlines a template which specifies the implementation of all vdk-core plugins. It includes a setup.py file, a /src/ directory containing all the plugin hooks and additional implementation files, a /tests/ directory containing all plugin-specific tests, and a .plugin-ci.yml file which specifies the CI/CD relevant to the plugins.


The CI/CD is separated in two stages, a build stage and a release stage. The build stage is made up of three jobs, all which inherit from the same job configuration and only differ in the Python version they use (3.7, 3.8 and 3.9). They run according to three rules, which are ordered in a way such that changes to a plugin's directory or the main directory triggers them, but changes to a different plugin do not.
