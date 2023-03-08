
- [REST API and Services](#rest-api-and-services)
- [Java](#java)
- [Python](#python)
  * [Clarification on access modifiers in python](#clarification-on-access-modifiers-in-python)
  * [Public Python interfaces](#public-python-interfaces)
  * [Development Status](#development-status)
- [CLI (Command Line interfaces)](#cli-command-line-interfaces)
- [Error handling](#error-handling)
- [README files](#readme-files)


We aim for:

* Code [maintainability](https://en.wikipedia.org/wiki/Maintainability)
* Low [coupling](https://en.wikipedia.org/wiki/Coupling_(computer_programming)#Types_of_coupling) and high [cohesion](https://en.wikipedia.org/wiki/Cohesion_(computer_science)#Types_of_cohesion)
* Simplicity (don't overengineer)

VDK coding styles aim for code style and formatting consistent across its components. The value of consistency is enabling automated formatting, avoiding back and forth reformatting, and making the code easy to read for all contributors. 

## REST API and Services 

We follow [12 factor app](https://12factor.net) recommendation for building web/api services. Make sure you have read and are familiarized with the document.

The rules outlined in https://opensource.zalando.com/restful-api-guidelines/ are recommended read and nice to follow but not a must.

## Java 
We follow [Google Java Coding style](https://google.github.io/styleguide/javaguide.html) and it is enforced by a pre-commit hook.

## Python

The coding standard is the Python regular [PEP 8](https://www.python.org/dev/peps/pep-0008/). It's enforced by [pre-commit hooks](https://github.com/vmware/versatile-data-kit/blob/main/.pre-commit-config.yaml#L18) like [black](https://github.com/psf/black).

### Clarification on access modifiers in python

Python uses `_` (underscore) symbol to determine the access control for a specific data member or a member function of a class
- Public methods have not underscore prefix
- Protected methods or attributes have single underscore as prefix - for example `_execute_protected()`
- Private methods or attributes have double underscore as prefix - for example `__execute_private()`

### Public Python interfaces 

Any backwards compatibility guarantees apply only to public interfaces. Public interfaces are modules and packages defined or imported in vdk.api.*. unless the documentation explicitly declares them to be provisional or internal interfaces. Anything else is considered internal. All public interfaces (classes or methods) must have documentation.
The documentation must specify clearly: 
* What is the purpose of the method/class
* What are the possible effects and side effects
* For each argument what are the preconditions 
* Example usages 

### Development Status 

Each public python distribution (for example a vdk plugin) should be classified based on its development status. 
* In setup.py (or setup.cfg) define classifier "Development Status" as defined in https://pypi.org/classifiers.  
* The semantics of the "Development Status" classifier are same as one defined in https://martin-thoma.com/software-development-stages 

## CLI (Command Line interfaces)

CLI is built following [12 Factor CLI Apps](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46). Make sure you have read and are familiarized with the document.
 
Summarized those are:
1. Great help is essential. Every command and option should have detailed help and examples. 
2. Prefer flags (key/value input) to arguments (positional input)
3. Version option/comand
4. Stdout is for data and output and stderr is for logs and messages!
5. Make errors informative. Basically follow [VDK error guidelines](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/CONTRIBUTING.md#error-handling)
6. Be fancy if you can
7. Prompt if you can
8. Use tables but allow output in csv or json
9. Be speedy (< 1 second respond time!)
10. Encourage contributions 
11. Be clear about subcommands
12. Follow [XDG-spec](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) for config or data files.



## Error handling 

Errors should not explain our (the developer) problem. Explain their (the user, and sometimes the caller) problem, and provide info valuable for THEM to understand what actions to take.

Make sure you follow [Error handling format](https://github.com/vmware/versatile-data-kit/blob/main/projects/control-service/CONTRIBUTING.md#error-handling) which aims to help write clearer and more consistent error messages.

## README files

Each VDK [project](https://github.com/vmware/versatile-data-kit/tree/main/projects) or [plugin](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins) has a README file that resides in its root folder and is named README.md. Each independentally releasable sub-component (e.g plugin, job-builder, job-base image) must have a README file as well.

A README file is written in [Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).

A README file of a project or a plugin should contain (whichever is applicable):

- what the project is about (e.g. its purpose);
- how to install the project (e.g. how to install and configure its dependencies);
- how to configure the project (e.g. where the configuration file resides, and what each configuration property means);
- how to build the project (e.g. how to compile its source code);
- how to use it (e.g. what command to execute and examples).
 
