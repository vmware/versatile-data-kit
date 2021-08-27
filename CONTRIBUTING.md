The Versatile Data Kit project team welcomes contributions from the community.

If you wish to contribute code and you have not signed our contributor license agreement ([CLA](https://cla.vmware.com/cla/1/preview)),
our bot will update the issue when you open a Pull Request.
For any questions about the CLA process, please refer to our [FAQ](https://cla.vmware.com/faq).

# Structure of the project

* projects - the interesting part, aka the source code - there is a separate folder for each component.
  * control-service - Java spring-based API for managing lifecycle of data jobs: job definitions, job deployments, and executions in Kubernetes.
  * vdk-core - Python-based SDK containing data library for developing and running data jobs. Includes a powerful plugin framework .
  * vdk-heartbeat - tool for verifying deployed SDK and Control Service are functional and working correctly
  * vdk-control-cli - User friendly CLI interface over Control Service operations including login/logout.
  * vdk-core/plugins - Set of plugins that we maintain and provide for different use-cases like lineage, database support, ...
* support - helper scripts used by developers of the project during their workday
* cicd - build and ci cd related scripts common across all projects. Each project also has its own cicd folder
* examples - list of example use-cases. Each example directory has its README with detailed explanations
* specs - specs for feature proposals and architecture documents

# How to build, debug

To boostrap the project run
```bash
./cicd/build.sh
```

Each component project is independently buildable and has independent CICD.
This enables people to contribute only to specific component without needing to know anything about the other components.

Each component project has its own README.md with specific details on how to test (locally), build it, and run it.
Each component project also have "build.sh" scripts in their cicd/ folder that would build the whole component.
Each component project also have its own .gitlab-ci.yml file with CICD definition.

If in doubt, open the .gitlab-ci.yml file of the project.
Read through the Gitlab CI file to find the build process confirmed to work by an automated continuous integration (CI).
CI runs in Docker Linux containers, so if you have docker installed, you will be able to replicate the process.

# How to prepare your change

Versatile Data Kit project uses GitHub issues and pull requests to track what work needs to be done,
what work is currently in progress, who work is assigned to.

Before suggesting a change/feature, think if this change only serves your needs, or it is broader,
that is good for the project itself because it helps multiple users.

For more complex features/changes, submitting your design is valuable, if possible, before you even write a single line of code.
Creating a PR in Github with your proposal as markdown (in [specs](specs) directory) is recommended.
Reviews and feedback will happen on the PR.

Also, reach out to the community - through slack, mail to discuss your idea. We are happy to help.

# How to submit and merge

We use [Github Flow](https://docs.github.com/en/get-started/quickstart/github-flow).
In short, it looks like this:
- All changes to the main branch ("main" in our case) are through pull requests.
- Any changes must go on a feature branch or on a fork.
- Pipeline must pass before merging, and the pull request must be [reviewed](https://docs.github.com/en/github/collaborating-with-pull-requests/reviewing-changes-in-pull-requests) and approved.
- Break code commits into small self-contained units
- Commit messages must follow the template in [git-commit-template.txt](support/git-commit-template.txt).
  We aim to follow https://chris.beams.io/posts/git-commit
- projects/*/CHANGELOG.md Next version section should be updated accordingly.

We prefer maintaining a straight branch history by rebasing before merging. Fast-forward merges should not create merge commits.

# Changelog
It's important to update [CHANGELOG](CHANGELOG.md) with any adjustments to the project.
Versioning of all components follow https://semver.org

Changelog has the following sections:
- New feature: significant additions to the project. This usually requires bumping at least a minor version.
- Improvements - an enhancement to existing functionality and minor additions
- Bug Fixes - Fixes of bugs/regressions
- Breaking Changes: any changes that break Versatile Data Kit's backward-compatibility

# CI

We are using CI as a code based on Gitlab CI.
Entrypoint of CICD is the file .gitlab-ci.yml.

There you can find the full definition of the CI/CD pipeline.
