<p align="center">
    <a href="https://github.com/vmware/versatile-data-kit">
        <img src="https://gitlab.com/vmware-analytics/versatile-data-kit/badges/main/pipeline.svg" alt="build status"></a>
    <a href="https://bestpractices.coreinfrastructure.org/projects/5363">
        <img src="https://bestpractices.coreinfrastructure.org/projects/5363/badge"></a>
    <a href="https://app.codacy.com/gh/vmware/versatile-data-kit?utm_source=github.com&utm_medium=referral&utm_content=vmware/versatile-data-kit&utm_campaign=Badge_Grade_Settings">
        <img src="https://api.codacy.com/project/badge/Grade/fac902e4672543b697da5311b565113e"></a>
<!-- TODO: code coverage -->
</p>

# First Steps to Contributing

Contributing to an open source project is a great way to build skills, make connections, and gain experience.
Here are the first steps to becoming a contributor:

1. You can connect with us on our [Slack Channel](#contact-us) - let us know you wish to contribute, and we'll get you started.
2. Check out our [good first issues](https://github.com/vmware/versatile-data-kit/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).
3. Try out VDK and tell us what you think by scheduling an [informal 30-minute call with us](https://outlook.office365.com/owa/calendar/VersatileDataKit1@onevmw.onmicrosoft.com/bookings/s/JFPGSXpR7kG30yukLR4fZA2).
4. Start with [our documentation](https://github.com/vmware/versatile-data-kit/wiki) and enhance it.
5. Read a simple [step-by-step guide by GitHub](https://github.com/firstcontributions/first-contributions).


# Ways to Contribute
We welcome many different types of contributions, including:
- Adding new features and proposals
- Creating and updating documentation
- Writing design specifications
- Creating visual graphics
- Identifying and fixing bugs
- Triaging issues
- Answering questions and providing feedback
- Helping onboard new contributors
- Creating content - blogs, videos, etc.

# Code of Conduct
VDK follows the [Code of Conduct](https://github.com/vmware/versatile-data-kit/blob/main/CODE_OF_CONDUCT.md), adapted from the [Contributor Covenant](https://www.contributor-covenant.org/). Please read the Code of Conduct guide to familiarize yourself with the expectations and responsibilities of the community.

# Contributor License Agreement CLA.
If you wish to contribute code, you must sign the [contributor license agreement](https://cla.vmware.com/cla/1/preview) (CLA). For any questions about the CLA process, please refer to our [FAQ](https://cla.vmware.com/faq) page.

# Structure of the repository

Our repository is organized as a monorepo, meaning it houses multiple [projects](https://github.com/vmware/versatile-data-kit/tree/main/projects) and [plugins](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins) within the same repository.

You can find each [individual project](https://github.com/vmware/versatile-data-kit/tree/main/projects) and [plugin](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins) located in their respective directories.
The design of our monorepo allows for each project and plugin to be developed independently.

What this means for your workflow is that when you want to work on a specific project or plugin, you only need to load that particular one into your IDE, rather than the entire monorepo.
This should make it easier to focus on your specific task without getting lost in the entire codebase.


# Design Principles and Architecture
[Familiarize with Versatile Data Kit Design Principles](https://github.com/vmware/versatile-data-kit/wiki/Design-Principles).
We want to prioritize user-centered development, seamless user experience, and data-centric interfaces.

[Familiarize with Versatile Data Kit Architecture](https://github.com/vmware/versatile-data-kit/tree/main/specs/architecture)

# Coding Standard
See [Versatile Data Kit Coding Standard](https://github.com/vmware/versatile-data-kit/wiki/Coding-Standard).

# Pull Requests
All contributors follow GitHub’s pull request (PR) workflow to submit changes. Before merging, all pull requests require two approvals.


# Branch Naming Convention
Our branches follow the naming convention: `person/<username>/<feature-name>`


# Semantic Versioning
VDK follows semantic versioning standards as part of https://semver.org/.

Given a version number MAJOR.MINOR.PATCH, increment the:
- MAJOR version when you make incompatible API changes
- MINOR version when you add functionality in a backward-compatible manner
- PATCH version when you make backwards-compatible bug fixes

# Dependencies Licencing

Here you can see what licenses are dependencies of Versatile Data Kit: [Dependencies Licencing](https://github.com/vmware/versatile-data-kit/wiki/Dependencies-licensing).

# Bugs
## Where to Find Known Issues
Review the [list of existing issues](https://github.com/vmware/versatile-data-kit/issues) to see if the bug has already been reported.


## Reporting New Issues
To report a bug, [create a GitHub issue](https://github.com/vmware/versatile-data-kit/issues). Include steps to replicate the bug in the issue description.


## Security Bugs
If you believe you have found a security bug, reach out to us first using any method in the [Contact Us](#contact-us) section and [create a GitHub issue](https://github.com/vmware/versatile-data-kit/issues).


# Propose a Change
Before proposing a feature or change, consider the impact of this change. Does it only serve your needs, or does it serve the broader community's needs?

For substantial features or changes, submitting your design is valuable.

To submit a change:
1. Create a PR in Github.
2. Follow the [VDK Enhancement Proposal (VEP)](https://github.com/vmware/versatile-data-kit/tree/main/specs) template.
3. Add your proposal as markdown in the [/specs](https://github.com/vmware/versatile-data-kit/blob/main/specs) directory.

Reviews, feedback, and approvals are documented in the PR.

Reach out to the community through Slack or e-mail in the [Contact Us](#contact-us) section to discuss your idea. We are happy to help.

# Development Workflow
A typical development workflow has the following process:
- Create a topic branch from where you want to base your work, naming your branch according to our naming convention. For example, `person/<github-username>/<feature-name>`.
- Make commits in logical units.
- Use clear commit titles and commit descriptions.
- Push your changes to the topic branch in your fork.
- Create a pull request from the commit.

We follow the GitHub workflow. See [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow) for more information.

**Note**: Use forks only for examples and documentation contributions.
  Currently, we accept contributions from forks only for examples and documentation changes until PR [854](https://github.com/vmware/versatile-data-kit/issues/854) is fixed. Until then, please request write privileges and create a branch in the main repository.

# IDE and Testing Locally
There is no global IDE and testing setup because each plugin and project has its own development and setup guide.
You can find these in the CONTRIBUTING.md for each project.

Follow the guides on how to setup IDE, build, test, run, and release - for [vdk-core](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/CONTRIBUTING.md#local-build) and [vdk-control-cli](https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-control-cli/CONTRIBUTING.md#build)

Here you can find a guide to [Setting up GPG key for signing commits](https://github.com/vmware/versatile-data-kit/wiki/Dev-How-tos#setting-up-gpg-key-for-signing-commits)

# Testing
Follow the guide on [GitLab CI/CD](https://github.com/vmware/versatile-data-kit/wiki/Gitlab-CICD)

# Your First Pull Request
If this is your first PR, take a look at this video series to get you started:
[How to Contribute to an Open Source Project on GitHub](https://egghead.io/courses/how-to-contribute-to-an-open-source-project-on-github).

Take a look at our list of [good first issues](https://github.com/vmware/versatile-data-kit/labels/good%20first%20issue). These issues are a great place to start.

If you see an issue that you would like to work on, leave a comment in the issue to let people know you are interested.

## Submit and merge a change
Before submitting your first PR, please review our general guidelines in [How to prepare a new PR](https://github.com/vmware/versatile-data-kit/wiki/How-to-prepare-a-new-PR).

## Pull Request Checklist
Before submitting your pull request, review the following:
- [ ] Check if your code changes pass code linting checks and unit tests.
- [ ] Ensure your commit messages are descriptive. Be sure to include any related GitHub issue references in the commit message. See [Basic writing and formatting syntax](https://guides.github.com/features/mastering-markdown/) for guidelines on syntax formatting.
- [ ] Check the commit and commit messages to ensure they are free from spelling and grammar errors.
- [ ] Use clear commit titles and commit descriptions for generating changelog release notes.

## Submit a pull request
- All changes must be submitted to the main branch using pull requests.
- Any change must go on a feature branch or on a fork.
- Pipeline must pass before merging.
- Code commits must be broken down into small self-contained units.
- Commit messages must follow the template in [git-commit-template.txt](https://github.com/vmware/versatile-data-kit/blob/main/support/git-commit-template.txt). See [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit) as a guideline to writing commit messages.
- The change must abide by the [Versatile Data Kit Coding Standard](https://github.com/vmware/versatile-data-kit/wiki/Coding-Standard).
- Each change is subject to two code reviews and approvals before it is merged.

We prefer to maintain a straight branch history by rebasing before merging. Fast-forward merges should not create merge conflicts.

# Documentation Guide
To document your changes, follow the [Documentation Guide](https://github.com/vmware/versatile-data-kit/wiki/Documentation-Guide)

# Next Steps
Ready to contribute? Look at the [open issues list](https://github.com/vmware/versatile-data-kit/issues) or create an issue for a suggested change.

# Contact us
You can reach out to us using any of the following:
- Connect on Slack by:
    - Joining the [CNCF Slack workspace](https://communityinviter.com/apps/cloud-native/cncf).
    - Joining the [#versatile-data-kit](https://cloud-native.slack.com/archives/C033PSLKCPR) channel.
- Follow us on [Twitter](https://twitter.com/VDKProject).
- Join our [development mailing list](mailto:join-versatiledatakit@groups.vmware.com), used by developers and maintainers of VDK.
