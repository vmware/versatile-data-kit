<p align="center">
    <a href="https://github.com/vmware/versatile-data-kit">
        <img src="https://gitlab.com/vmware-analytics/versatile-data-kit/badges/main/pipeline.svg" alt="build status"></a>
    <a href="https://bestpractices.coreinfrastructure.org/projects/5363">
        <img src="https://bestpractices.coreinfrastructure.org/projects/5363/badge"></a>
    <a href="https://app.codacy.com/gh/vmware/versatile-data-kit?utm_source=github.com&utm_medium=referral&utm_content=vmware/versatile-data-kit&utm_campaign=Badge_Grade_Settings">
        <img src="https://api.codacy.com/project/badge/Grade/fac902e4672543b697da5311b565113e"></a>
<!-- TODO: code coverage -->
</p>

# Contributing to Versatile Data Kit

We welcome contributions from the community and first want to thank you for taking the time to contribute!

Please familiarize yourself with the [Code of Conduct](https://github.com/vmware/versatile-data-kit/blob/main/CODE_OF_CONDUCT.md) before contributing.

* _CLA: Before you start working with Versatile Data Kit, please read and sign our Contributor License Agreement [CLA](https://cla.vmware.com/cla/1/preview). If you wish to contribute code and you have not signed our contributor license agreement (CLA), our bot will update the issue when you open a Pull Request. For any questions about the CLA process, please refer to our [FAQ]([https://cla.vmware.com/faq](https://cla.vmware.com/faq))._

## Ways to contribute

We welcome many different types of contributions and not all of them need a Pull request. Contributions may include:

* New features and proposals
* Documentation
* Bug fixes
* Issue Triage
* Answering questions and giving feedback
* Helping to onboard new contributors
* Other related activities

# Getting Started

## Contribution Flow

This is a rough outline of what a contributor's workflow looks like:

* Use forks to only contribute changes on examples and documentation.
   * Currently we accept contribution from forks only for examples and documentation changes until PR 854 is fixed. Until then please request write priveleges and create a branch in the main repo as described below.
* Create a topic branch from where you want to base your work - name your branch according to our naming convention - person/<github-username>/<feature-name>
* Make commits of logical units
* Make sure your commit messages are with the proper format, quality and descriptiveness (see below)
* Push your changes to the topic branch in your fork
* Create a pull request containing that commit

We follow the GitHub workflow and you can find more details on the [GitHub flow documentation](https://docs.github.com/en/get-started/quickstart/github-flow).

## Structure of the project

* projects - the interesting part, aka the source code - there is a separate folder for each component;
  * control-service - Java spring-based API for managing the lifecycle of data jobs: job definitions, job deployments, and executions in Kubernetes;
  * vdk-core - Python-based SDK containing a data library for developing and running data jobs. Includes a powerful plugin framework;
  * vdk-heartbeat - tool for verifying the deployed SDK and Control Service are functional and working correctly;
  * vdk-control-cli - User friendly CLI interface over Control Service operations including login/logout;
  * vdk-plugins - Set of plugins that we maintain and provide for different use-cases like lineage, database support, etc.;
  * frontend - Angular web UI for creating, deploying and managing jobs.
* support - helper scripts used by developers of the project during their workday;
* cicd - build and ci cd related scripts common across all projects. Each project also has its own cicd folder;
* examples - list of example use-cases. Each example directory has its README with detailed explanations;
* specs - specs for feature proposals and architecture documents;
* events - details about the conferences/workshops where VDK was presented.

## How to build, debug

To boostrap the project run
```bash
./cicd/build.sh
```

Each component project is independently buildable and has independent CICD.
This enables people to contribute only to a specific component without needing to know anything about the other components.

Each component project has its own README.md with specific details on how to test (locally), build, and run it.
Each component project also has "build.sh" scripts in their cicd/ folder that would build the whole component.
Each component project also has its own .gitlab-ci.yml file with a definition of its CICD.

If in doubt, open the .gitlab-ci.yml file of the project.
Read through the Gitlab CI file to find the build process confirmed to work by an automated continuous integration (CI).
CI runs in Docker Linux containers, so if you have docker installed, you will be able to replicate the process.

## How to prepare your change

Versatile Data Kit project uses GitHub issues and pull requests to track what work needs to be done,
what work is currently in progress, and who work is assigned to.

Before suggesting a change/feature, think if this change only serves your needs, or it serves a broader need,
which is good for the project itself because it helps multiple users.

For more complex features/changes, submitting your design is valuable, if possible, before you even write a single line of code.
Creating a PR in Github with your proposal as markdown (in [specs](specs) directory) is recommended.
Reviews and feedback will happen in the PR.

Also, reach out to the community - through Slack or mail to discuss your idea. We are happy to help.

## Coding Standard
The Versatile Data Kit Coding Standard can be found [here](https://github.com/vmware/versatile-data-kit/wiki/Coding-Standard).

## How to submit and merge

We use [Github Flow](https://docs.github.com/en/get-started/quickstart/github-flow).
In short, it looks like this:
- All changes to the main branch ("main" in our case) are through pull requests;
- Any changes must go on a feature branch or on a fork;
- Pipeline must pass before merging, and the pull request must be [reviewed](https://docs.github.com/en/github/collaborating-with-pull-requests/reviewing-changes-in-pull-requests) and approved;
- Break code commits into small self-contained units;
- Commit messages must follow the template in [git-commit-template.txt](support/git-commit-template.txt).
  We aim to follow https://chris.beams.io/posts/git-commit;
- The change must abide by the [Coding Standard](https://github.com/vmware/versatile-data-kit/wiki/Coding-Standard);
- Each change is a subject to 2 code reviews for it to be merged (experimental).

Familiarize with [recommendations written here](https://github.com/vmware/versatile-data-kit/wiki/How-to-prepare-a-new-PR).

We prefer maintaining a straight branch history by rebasing before merging. Fast-forward merges should not create merge commits.

## Changelog
Versioning of all components follows https://semver.org

For generating release notes (changelog) we rely on good commit titles and commit descriptions (see above section).

## Pull Request Checklist

Before submitting your pull request, we advise you to use the following:

1. Check if your code changes will pass both code linting checks and unit tests.
2. Ensure your commit messages are descriptive. Be sure to include any related GitHub issue references in the commit message. See [GFM syntax](https://guides.github.com/features/mastering-markdown/#GitHub-flavored-markdown) for referencing issues and commits.
3. Check the commits and commits messages and ensure they are free from typos.

## CI

We are using CI as a code based on Gitlab CI.
Entrypoint of CICD is the file .gitlab-ci.yml.

There you can find the full definition of the CI/CD pipeline.
For more details see the [CICD wiki in our Dev Guide](https://github.com/vmware/versatile-data-kit/wiki/Gitlab-CICD)

## How to make a new VDK release

See previous releases: https://github.com/vmware/versatile-data-kit/releases
A release is a certain milestone of VDK where we share the latest changes with the community.
We aim to make a new public release every few weeks.

To make a new public release, follow these steps:
- Create a new release from the Releases menu - this will require a new tag;
- Autogenerate the changelog (https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes), then sort the changes alphabetically; if all change names are prefixed with the component name, this will ensure changes are grouped by component. Sorting can be done using the `sort` utility available in MacOS and Linux distros; Clean up unnecessary commits (e.g automated commits like pre-commit.ci)
- Write a summary at the top of the release page. It should include sections:
  - Major features include
  - Backwards incompatible changes
  - Removal of features
- Review which components have received changes since the previous release - this should be apparent from the changelog;
- Record the latest versions of the components included in the release (from the auto generated notes) and list them in the Release description;
    - You can see the current version (as of time of release) of a Python package in https://pypi.org/search/?q=
    - You can see the current version (as of time of release) of the Control Service in [the helm repo here](https://gitlab.com/vmware-analytics/versatile-data-kit-helm-registry/-/packages)
- Make sure you have clicked the "Create a discussion for this release" button before publishing the new release
- Post a tweet on the official VDK Twitter account, and on slack, announcing the new release and linking to it.


## Ask for Help

The best way to reach us with a question when contributing is to ask on:

* The original GitHub issue
* [Our Slack channel](https://cloud-native.slack.com/archives/C033PSLKCPR)
* Join our [Community Meetings](https://github.com/vmware/versatile-data-kit/wiki/Community-Meeting-and-Open-Discussion-Notes)
