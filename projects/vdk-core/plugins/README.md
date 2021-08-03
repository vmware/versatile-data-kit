Here we keep the default plugins that will be built by the team as a reference implementations for different use-cases.

In order to add a new plugin , copy the plugin-template directory and follow the instructions in the files
Generally those are
 * Update setup.py file with correct name of the plugin app
 * Update .plugin-ci.yml file with name of the plugin - make sure to follow comments.
 * src folder is which contain the source code of your plugin
 * tests folder will contain tests which will be run by CI framework automatically.
