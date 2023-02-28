# Managing VDK Data Jobs in a directed acyclic graph using Meta Jobs

### Intro

Modern data pipelines are comprised of many workloads of different types which often are interdependent on each other. Versatile Data Kit has provided greater atomization to individual data workloads through its Data Jobs API, and now with the release of the vdk-meta-jobs package, VDK offers the ability to express Data Job dependencies in an idiomatic fashion through managing workloads called Meta Jobs.

### Meta Jobs Overview

Meta Jobs use a new job_input API which allows them to start and monitor job executions of jobs whose interdependencies can be expressed as a directed acyclic graph. What this means is that a user can now execute a set of jobs where one job waits for multiple other to complete before starting, or vice versa, or any other arbitrary structure of job dependencies; the execution monitoring is all done by one workload, which is called a Meta Job.
Meta Jobs are still deployed as a VDK Data Job, and as such offer the same feature set that other jobs do. They can be scheduled to run daily, hourly, etc. through a cron-schedule configuration parameter, they include logs which include a breakdown of all the component jobs and links to their logs


### Installation/Setup

TODO

### Meta Jobs demo

TODO *summary of the example*
TODO *also link to the example for details, don’t want to overwhelm the reader*


### Outro/What’s next

TODO
