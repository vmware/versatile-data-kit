![Versatile Data Kit](./support/images/versatile-data-kit.svg#gh-light-mode-only)
![Versatile Data Kit](./support/images/versatile-data-kit.svg#gh-dark-mode-only)

<p align="center">
    <a href="https://github.com/vmware/versatile-data-kit/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/vmware/versatile-data-kit" /></a>
    <a href="https://github.com/vmware/versatile-data-kit/contributors" alt="Last Activity">
        <img src="https://img.shields.io/github/last-commit/vmware/versatile-data-kit" alt="Last Activity"></a>
    <a href="https://github.com/vmware/versatile-data-kit/blob/main/LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/vmware/versatile-data-kit" alt="license"></a>
    <a href="https://github.com/pre-commit/pre-commit">
        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="pre-commit"></a>
    <a href="https://github.com/vmware/versatile-data-kit">
        <img src="https://gitlab.com/vmware-analytics/versatile-data-kit/badges/main/pipeline.svg" alt="build status"></a>
    <a href="https://twitter.com/intent/tweet?text=Wow: @VDKProject">
        <img src="https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2FVDKProject" alt="twitter"/></a>
     <a href="https://www.youtube.com/channel/UCasf2Q7X8nF7S4VEmcTHJ0Q">
        <img alt="YouTube Channel Subscribers" src="https://img.shields.io/youtube/channel/subscribers/UCasf2Q7X8nF7S4VEmcTHJ0Q?style=social"></a>

<!-- TODO: code coverage -->
</p>


# Overview
Versatile Data Kit (VDK) is an open source framework that enables anyone with basic SQL or Python knowledge to build, run, and manage their own data workflows.

Data processing instructions use plain text SQL or python files that are executed sequentially in alphanumeric order, allowing you to easily build your data workflows.

VDK is built for resiliency and can recover in mid-process or restart entirely from the start.


# Data Journey and Versatile Data Kit
VDK creates data processing workflows to:
- Ingest data (extract)
- Transform data (transform)
- Export data (load)


![Data Journey](./support/images/versatile-data-kit-data-journey.svg#gh-light-mode-only)
![Data Journey](./support/images/versatile-data-kit-data-journey-dark-mode.svg#gh-dark-mode-only)


# Solve common data engineering problems
- Ingest data from different sources, including CSV files, JSON objects, and data from REST API services.
- Use Python/SQL and VDK templates to transform data.
- Ensure data applications are packaged, versioned, and deployed correctly while dealing with credentials, retries, and reconnects.
- Provide built-in monitoring and smart notification capabilities.
- Track both code and data modifications and the relationship between them, allowing quicker troubleshooting and version rollback.


![Without / With Versatile Data Kit](./support/images/versatile-data-kit-before-after-light.svg#gh-light-mode-only)
![Without / With Versatile Data Kit](./support/images/versatile-data-kit-before-after-dark.svg#gh-dark-mode-only)

# Versatile Data Kit Components
- Software Development Kit (SDK):
    - Tools to automate the extraction, transformation, and loading of data.
    - A plugin framework that allows users to extend the framework according to their specific requirements.

![](https://github.com/vmware/versatile-data-kit/blob/person/zverulacis/gif/support/images/versatile-data-kit-help.gif)

- Control Service: The Control Service allows users to create, deploy, manage, and execute data jobs in a Kubernetes runtime environment.


# Getting Started
Installing VDK is a simple pip command. See the [Getting Started](https://github.com/vmware/versatile-data-kit/wiki/getting-started) guide to install VDK and create a data job.

# Next Steps
- See [use case examples](https://github.com/vmware/versatile-data-kit/wiki/Examples) that show how VDK fits into the data workflow.
- See the [documentation](https://github.com/vmware/versatile-data-kit/wiki/Introduction) for VDK.
- Read the article about [using the Versatile Data Kit and Trino DB](https://towardsdatascience.com/from-raw-data-to-a-cleaned-database-a-deep-dive-into-versatile-data-kit-ab5fd992a02e).
- Join us at a [community meeting](https://github.com/vmware/versatile-data-kit/wiki/Community-and-Resources)

# Contributing
Create an [issue](https://github.com/vmware/versatile-data-kit/issues) or [pull request](https://github.com/vmware/versatile-data-kit/pulls) on GitHub to submit suggestions or changes. If you are interested in contributing as a developer, visit the [contributing](https://github.com/vmware/versatile-data-kit/blob/main/CONTRIBUTING.md) page.

# Contacts
- Connect on Slack by:
    1. Joining the [CNCF Slack workspace](https://communityinviter.com/apps/cloud-native/cncf).
    2. Joining the [#versatile-data-kit](https://cloud-native.slack.com/archives/C033PSLKCPR) channel.
- Follow us on [Twitter](https://twitter.com/VDKProject).
- Subscribe to the [Versatile Data Kit YouTube Channel](https://www.youtube.com/channel/UCasf2Q7X8nF7S4VEmcTHJ0Q).
- Join our [development mailing list](mailto:join-versatiledatakit@groups.vmware.com), used by developers and maintainers of VDK.

# Code of Conduct
Everyone involved in working on the project's source code, or engaging in any issue trackers, Slack channels, and mailing lists is expected to be familiar with and follow the [Code of Conduct](https://github.com/vmware/versatile-data-kit/blob/main/CODE_OF_CONDUCT.md).
