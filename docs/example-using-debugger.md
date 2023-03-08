# Setup a debugger using VDK

## Visual Studio Code 

1. [Install VDK](./Installation)
2. In VSCode go to debug (Ctrl+Shift+D) and go to options (launch.json)
3. Add the following configuration
```
{
    "configurations": [
        {
            "name": "Python: VDK",
            "type": "python",
            "request": "launch",
            "module": "vdk.internal.cli_entry",
            "args": [
                "run",
                "${workspaceFolder}"
            ],
        }
    ]
}
```
4. [Select interpreter](https://code.visualstudio.com/docs/python/environments#_select-and-activate-an-environment) where vdk is installed : 

![](https://code.visualstudio.com/assets/docs/python/environments/select-interpreters-command.png)

## IntelliJ

1. [Install VDK](./Installation)

2. Setup Project SDK to the python virtual environment setup (where vdk is installed) in Step 1. 

![](https://github.com/vmware/versatile-data-kit/wiki/docs/intellij-vdk-add-python.png).

3. Create a new project with the root the data job directory. And set the Project SDK created in Step 2.

![](https://github.com/vmware/versatile-data-kit/wiki/docs/intellij-vdk-set-project-sdk.png).

4. IntelliJ run configuration should look like below screenshot (data job's name is "foo-job"):
 - module name must be `vdk.internal.cli_entry`
 - parameter `run .`
 - Working directory should point to the data job directory
 - If necessary set the project SDK configured in step 2 and 3 as Interpreter

![](https://github.com/vmware/versatile-data-kit/wiki/docs/intellij-vdk-run-configuration.png).



